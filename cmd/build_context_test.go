// Copyright 2026 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

//go:build unix

package cmd

import (
	"archive/tar"
	"bytes"
	"errors"
	"io"
	"os"
	"path/filepath"
	"reflect"
	"strings"
	"syscall"
	"testing"
)

func TestLocalBuildArgsStreamsContextOnlyForDocker(t *testing.T) {
	args, stdin := localBuildArgs("docker", "base:1", "out:1", "", "/home/u/.scion/harness-configs/pi")
	want := []string{"build", "--build-arg", "BASE_IMAGE=base:1", "-t", "out:1", "-"}
	if !stdin || !reflect.DeepEqual(args, want) {
		t.Fatalf("docker: got %v stdin=%v, want %v stdin=true", args, stdin, want)
	}
	for _, bin := range []string{"podman", "container"} {
		args, stdin = localBuildArgs(bin, "base:1", "out:1", "linux/amd64", "/ctx")
		want = []string{"build", "--build-arg", "BASE_IMAGE=base:1", "-t", "out:1", "--platform", "linux/amd64", "/ctx"}
		if stdin || !reflect.DeepEqual(args, want) {
			t.Fatalf("%s: got %v stdin=%v, want %v stdin=false", bin, args, stdin, want)
		}
	}
}

func TestWriteBuildContextTarPacksRelativeTreeWithLinks(t *testing.T) {
	dir := filepath.Join(t.TempDir(), ".hidden", "pi")
	if err := os.MkdirAll(filepath.Join(dir, "home"), 0o755); err != nil {
		t.Fatal(err)
	}
	files := map[string]string{"Dockerfile": "FROM scratch\n", "home/.bashrc": "echo hi\n"}
	for name, body := range files {
		if err := os.WriteFile(filepath.Join(dir, name), []byte(body), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	if err := os.Chmod(filepath.Join(dir, "home", ".bashrc"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.Symlink("Dockerfile", filepath.Join(dir, "link")); err != nil {
		t.Fatal(err)
	}

	var buf bytes.Buffer
	if err := writeBuildContextTar(&buf, dir); err != nil {
		t.Fatal(err)
	}
	got := map[string]string{}
	modes := map[string]int64{}
	links := map[string]string{}
	tr := tar.NewReader(&buf)
	for {
		hdr, err := tr.Next()
		if errors.Is(err, io.EOF) {
			break
		}
		if err != nil {
			t.Fatal(err)
		}
		if strings.HasPrefix(hdr.Name, "/") || strings.Contains(hdr.Name, "..") {
			t.Fatalf("entry %q is not relative to the context", hdr.Name)
		}
		if hdr.Uid != 0 || hdr.Gid != 0 {
			t.Fatalf("entry %q keeps host ownership %d:%d", hdr.Name, hdr.Uid, hdr.Gid)
		}
		modes[hdr.Name] = hdr.Mode
		switch hdr.Typeflag {
		case tar.TypeReg:
			body, _ := io.ReadAll(tr)
			got[hdr.Name] = string(body)
		case tar.TypeSymlink:
			links[hdr.Name] = hdr.Linkname
		}
	}
	if !reflect.DeepEqual(got, files) {
		t.Fatalf("files: got %v, want %v", got, files)
	}
	if links["link"] != "Dockerfile" {
		t.Fatalf("symlink not stored as a link: %v", links)
	}
	if _, ok := modes["home/"]; !ok {
		t.Fatalf("directory entry missing: %v", modes)
	}
	if modes["home/.bashrc"]&0o111 == 0 {
		t.Fatalf("executable bit lost: %o", modes["home/.bashrc"])
	}
}

func TestWriteBuildContextTarRefusesSpecialFiles(t *testing.T) {
	dir := t.TempDir()
	if err := syscall.Mkfifo(filepath.Join(dir, "fifo"), 0o644); err != nil {
		t.Skipf("mkfifo unsupported: %v", err)
	}
	err := writeBuildContextTar(io.Discard, dir)
	if err == nil || !strings.Contains(err.Error(), "unsupported file type") {
		t.Fatalf("want unsupported file type error, got %v", err)
	}
}
