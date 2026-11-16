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

package cmd

import (
	"archive/tar"
	"fmt"
	"io"
	"io/fs"
	"os"
	"path/filepath"
)

// localBuildArgs returns the argv (without the runtime binary) for a local
// harness-config image build, and whether the build context must be streamed
// on stdin as a tar archive.
//
// Docker gets its context on stdin ("-"): the docker CLI then never opens the
// harness-config directory itself. That matters for a confined docker CLI,
// such as the snap package, which cannot read hidden directories under $HOME
// (~/.scion/harness-configs/...) and failed with "open Dockerfile: no such
// file or directory". scion reads the directory and the CLI only reads stdin.
// Other runtimes (podman, Apple container) treat "-" differently, so they keep
// the directory argument.
func localBuildArgs(runtimeBin, baseImage, outputImage, platform, contextDir string) ([]string, bool) {
	args := []string{"build",
		"--build-arg", "BASE_IMAGE=" + baseImage,
		"-t", outputImage,
	}
	if platform != "" {
		args = append(args, "--platform", platform)
	}
	if runtimeBin == "docker" {
		return append(args, "-"), true
	}
	return append(args, contextDir), false
}

// writeBuildContextTar writes dir as an uncompressed tar archive with paths
// relative to dir, the layout `docker build -` expects (Dockerfile at the
// root). Symlinks are stored as links, never followed, matching how docker
// itself packs a directory context; other non-regular files are refused.
func writeBuildContextTar(w io.Writer, dir string) error {
	tw := tar.NewWriter(w)
	err := filepath.WalkDir(dir, func(path string, d fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		rel, err := filepath.Rel(dir, path)
		if err != nil {
			return err
		}
		if rel == "." {
			return nil
		}
		info, err := d.Info()
		if err != nil {
			return err
		}
		link := ""
		switch {
		case info.Mode()&fs.ModeSymlink != 0:
			if link, err = os.Readlink(path); err != nil {
				return err
			}
		case info.IsDir(), info.Mode().IsRegular():
		default:
			return fmt.Errorf("build context %s: unsupported file type %s", path, info.Mode().Type())
		}
		hdr, err := tar.FileInfoHeader(info, link)
		if err != nil {
			return err
		}
		hdr.Name = filepath.ToSlash(rel)
		if info.IsDir() {
			hdr.Name += "/"
		}
		// Ownership of the host files means nothing inside the image build.
		hdr.Uid, hdr.Gid, hdr.Uname, hdr.Gname = 0, 0, "", ""
		if err := tw.WriteHeader(hdr); err != nil {
			return err
		}
		if !info.Mode().IsRegular() {
			return nil
		}
		f, err := os.Open(path)
		if err != nil {
			return err
		}
		_, err = io.Copy(tw, f)
		closeErr := f.Close()
		if err != nil {
			return err
		}
		return closeErr
	})
	if err != nil {
		return fmt.Errorf("pack build context %s: %w", dir, err)
	}
	return tw.Close()
}
