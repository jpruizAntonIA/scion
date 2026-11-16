FILE:desk/tasks/task-fase-0-ir-scion-build-pasa-el-contexto-por-stdin-el-docker-snap-no-lee-scion.md
---
sldb:
  by: agent
  at: '2026-11-16T00:48:45Z'
  authority: generated
  via: save_document_payload
id: task-fase-0-ir-scion-build-pasa-el-contexto-por-stdin-el-docker-snap-no-lee-scion
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
current_node: ritual-execution
history: []
references: []
depends_on: []
pills: []
files:
- cmd/build.go
- cmd/build_context.go
- cmd/build_context_test.go
task_type: task.code
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# Fase 0 IR: scion build pasa el contexto por stdin (el docker snap no lee ~/.scion)

## Rationale

_Explain why this task exists or the business driver behind it._

En robocop2 docker es snap (29.8.0) y su CLI no puede abrir directorios ocultos de $HOME; `scion build <harness-config>` falla con 'open Dockerfile: no such file or directory' porque le pasa ~/.scion/harness-configs/<name> como contexto. Bloquea construir imágenes de harness para el piloto scion en el desk de IR (brief scion-piloto-ir, fase 0 punto 2).

## Goal

_Describe the concrete result this task must produce._

`scion build <harness-config>` construye con docker aunque el CLI de docker no pueda leer ~/.scion: scion empaqueta el directorio del harness-config como tar y lo pasa por stdin (`docker build ... -`). podman y Apple container conservan el directorio como argumento. `--dry-run` muestra el comando equivalente (`tar -C <dir> -cf - . | docker build ... -`).

## Scope

_State what is in scope and what is out of scope._

IN: cmd/build.go (rama local, no cloud-build) y un archivo nuevo cmd/build_context.go con localBuildArgs y writeBuildContextTar, más cmd/build_context_test.go. Los symlinks del contexto se guardan como links (como hace docker); fifos/sockets/dispositivos se rechazan; uid/gid del host no viajan. OUT: cloud-build, la configuración del docker de la máquina (cambiar a docker no-snap o mover su raíz es decisión de JP), otros comandos.

## Implementation Path

_Outline the expected implementation route or affected surface._

hcDir se obtiene como hoy con config.FindHarnessConfigDir(name, projectPath). localBuildArgs(runtimeBin, baseImage, outputImage, platform, contextDir) devuelve (argv, contextOnStdin): argv = [build, --build-arg, BASE_IMAGE=<baseImage>, -t, <outputImage>] + [--platform, <platform>] solo si platform no está vacío + un último argumento: '-' si runtimeBin == 'docker' (contextOnStdin = true), si no contextDir (false). Sin -f: el Dockerfile está en la raíz del contexto. Con stdin: io.Pipe; una goroutine llama writeBuildContextTar(pw, hcDir.Path) y cierra con pw.CloseWithError(err); buildExec.Stdin = pr. Si el tar falla después de arrancar docker, docker recibe un stream truncado, el build termina con error y scion devuelve 'build failed: ...'; el error del empaquetado es 'pack build context <dir>: <causa>'. writeBuildContextTar: rutas relativas a hcDir.Path con '/' (directorios con '/' final), symlinks como entradas TypeSymlink cuyo Linkname es os.Readlink tal cual (sin resolver ni validar, igual que docker), uid/gid 0 sin nombres; fifo/socket/dispositivo -> error 'build context <path>: unsupported file type <tipo>'. --dry-run imprime literalmente 'tar -C <hcDir.Path> -cf - . | ' + 'docker ' + argv unidos por espacios, sin comillas (mismo estilo que la salida anterior).

## Validation

_List the checks required before this task can close._

- cd scion && go test ./cmd -run 'TestLocalBuildArgs|TestWriteBuildContextTar' -count=1
- scion build <harness-config> --dry-run (binario del fork) imprime 'tar -C <dir> -cf - . | docker build ... -'
- scion build <harness-config> con docker snap termina con rc 0 y la imagen aparece en docker images

## Done When

_Name the observable condition that makes the task complete._

Los tests nuevos pasan y en robocop2 `scion build` del fork construye una imagen de harness desde ~/.scion/harness-configs sin copiar el contexto a mano.

FILE:desk/rituals/phase.md
---
id: ritual-phase
steps: []
tags:
- workspace:desk
---

# Phase ritual for dependency-layer execution

Run one horizontal layer of scion tasks whose prerequisites are satisfied and whose
planned changes do not overlap, then close the layer with integration validation,
pill reconciliation, and next-phase preparation.

Each task in the phase still closes with its own validation and its own commit;
the phase adds the pass that only makes sense once those tasks are integrated.

FILE:desk/rituals/execution.md
---
id: ritual-execution
steps: []
tags:
- workspace:desk
---

# Execution ritual

Review the board, bind the relevant pills, keep scope tight, and implement only the active task for scion.

FILE:desk/rituals/testing.md
---
id: ritual-testing
steps: []
tags:
- workspace:desk
---

# Testing ritual

Run the smallest relevant validation first, then broaden coverage when scion changes shared behavior.

FILE:desk/rituals/closeout.md
---
id: ritual-closeout
steps: []
tags:
- workspace:desk
---

# Closeout ritual

Close a scion task only after validation passes, any durable knowledge from bound pills is linked to an atom when needed, the board is updated, and the final change is ready to commit.

FILE:cmd/build.go
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
	"errors"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/GoogleCloudPlatform/scion/pkg/config"
	"github.com/GoogleCloudPlatform/scion/pkg/runtime"
	"github.com/spf13/cobra"
	"gopkg.in/yaml.v3"
)

var (
	buildTag       string
	buildBaseImage string
	buildPush      bool
	buildPlatform  string
	buildDryRun    bool
	buildBuilder   string
)

var buildCmd = &cobra.Command{
	Use:   "build <harness-config-name>",
	Short: "Build a container image from a harness-config Dockerfile",
	Long: `Build a container image from a Dockerfile bundled inside a harness-config directory.

The base image is resolved from the image_registry setting unless --base-image
is provided. After a successful build the harness-config's config.yaml image
field is updated to reference the built image.`,
	Args: cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		harnessConfigName := args[0]

		hcDir, err := config.FindHarnessConfigDir(harnessConfigName, projectPath)
		if err != nil {
			return fmt.Errorf("harness-config %q not found: %w", harnessConfigName, err)
		}
		if hcDir.Path == "" {
			return fmt.Errorf("harness-config %q does not have a local directory path", harnessConfigName)
		}

		dockerfilePath := filepath.Join(hcDir.Path, "Dockerfile")
		if _, err := os.Stat(dockerfilePath); err != nil {
			if os.IsNotExist(err) {
				return fmt.Errorf("harness-config %q does not contain a Dockerfile", harnessConfigName)
			}
			return fmt.Errorf("cannot access Dockerfile in harness-config %q: %w", harnessConfigName, err)
		}

		tag := buildTag

		var settings *config.VersionedSettings
		if buildBaseImage == "" || buildPush || buildBuilder == "cloud-build" {
			settings, _, err = config.LoadEffectiveSettings(projectPath)
			if err != nil {
				return fmt.Errorf("failed to load settings: %w", err)
			}
		}

		imageRegistry := ""
		if settings != nil {
			// SCION_IMAGE_REGISTRY beats every settings layer
			// (ptone/scion#3916).
			imageRegistry = config.ResolveImageRegistryLayers(
				settings.ImageRegistryLayers(profile, config.ImageRegistryFromEnv())).Value
		}

		baseImage := buildBaseImage
		if baseImage == "" {
			baseImage = "scion-base:" + tag
			if imageRegistry != "" {
				baseImage = imageRegistry + "/scion-base:" + tag
			}
		}

		if buildBuilder == "cloud-build" {
			return runCloudBuild(cmd, harnessConfigName, hcDir, tag, baseImage, imageRegistry, settings)
		}

		runtimeBin := runtime.DetectContainerRuntime()
		if runtimeBin == "" {
			return fmt.Errorf("no container runtime found (tried docker, podman, container)")
		}

		imageBaseName := harnessConfigName
		if hcDir.Config.Image != "" {
			name := hcDir.Config.Image
			if colonIdx := strings.LastIndex(name, ":"); colonIdx >= 0 {
				name = name[:colonIdx]
			}
			imageBaseName = name
		}

		outputImage := imageBaseName + ":" + tag
		if buildPush {
			if imageRegistry == "" {
				return fmt.Errorf("--push requires image_registry to be configured")
			}
			outputImage = imageRegistry + "/" + imageBaseName + ":" + tag
		}

		buildArgs, contextOnStdin := localBuildArgs(runtimeBin, baseImage, outputImage, buildPlatform, hcDir.Path)

		if buildDryRun {
			line := runtimeBin + " " + strings.Join(buildArgs, " ")
			if contextOnStdin {
				line = "tar -C " + hcDir.Path + " -cf - . | " + line
			}
			fmt.Println(line)
			return nil
		}

		buildExec := exec.CommandContext(cmd.Context(), runtimeBin, buildArgs...)
		buildExec.Stdout = os.Stdout
		buildExec.Stderr = os.Stderr
		if contextOnStdin {
			pr, pw := io.Pipe()
			buildExec.Stdin = pr
			go func() {
				pw.CloseWithError(writeBuildContextTar(pw, hcDir.Path))
			}()
			err := buildExec.Run()
			_ = pr.Close()
			if err != nil {
				return fmt.Errorf("build failed: %w", err)
			}
		} else if err := buildExec.Run(); err != nil {
			return fmt.Errorf("build failed: %w", err)
		}

		if buildPush {
			pushExec := exec.CommandContext(cmd.Context(), runtimeBin, "image", "push", outputImage)
			pushExec.Stdout = os.Stdout
			pushExec.Stderr = os.Stderr
			if err := pushExec.Run(); err != nil {
				return fmt.Errorf("push failed: %w", err)
			}
		}

		syncBuildToHub(harnessConfigName, hcDir)

		return nil
	},
}

type cloudBuildConfig struct {
	Steps   []cloudBuildStep  `yaml:"steps"`
	Options cloudBuildOptions `yaml:"options"`
	Timeout string            `yaml:"timeout"`
}

type cloudBuildStep struct {
	Name string   `yaml:"name"`
	ID   string   `yaml:"id"`
	Args []string `yaml:"args"`
	Env  []string `yaml:"env,omitempty"`
}

type cloudBuildOptions struct {
	DynamicSubstitutions bool   `yaml:"dynamicSubstitutions"`
	MachineType          string `yaml:"machineType"`
}

// runCloudBuild executes the build via gcloud builds submit.
func runCloudBuild(cmd *cobra.Command, harnessConfigName string, hcDir *config.HarnessConfigDir, tag, baseImage, imageRegistry string, settings *config.VersionedSettings) error {
	if _, err := exec.LookPath("gcloud"); err != nil {
		return fmt.Errorf("--builder cloud-build requires gcloud CLI to be installed and in PATH")
	}
	if imageRegistry == "" {
		return fmt.Errorf("--builder cloud-build requires image_registry to be configured")
	}

	gcpProject := resolveGCPProject(settings)
	if gcpProject == "" {
		return fmt.Errorf("no GCP project configured; set gcp_project_id in settings or run 'gcloud config set project <project>'")
	}

	imageBaseName := harnessConfigName
	if hcDir.Config.Image != "" {
		name := hcDir.Config.Image
		if colonIdx := strings.LastIndex(name, ":"); colonIdx >= 0 {
			name = name[:colonIdx]
		}
		imageBaseName = name
	}
	outputImage := imageRegistry + "/" + imageBaseName + ":" + tag

	platform := buildPlatform
	if platform == "" {
		platform = "linux/amd64,linux/arm64"
	}

	// Build the cloudbuild.yaml via structured marshaling.
	cbConfig := cloudBuildConfig{
		Steps: []cloudBuildStep{
			{
				Name: "gcr.io/cloud-builders/docker",
				ID:   "setup-buildx",
				Args: []string{"buildx", "create", "--name", "builder", "--use"},
				Env:  []string{"DOCKER_CLI_EXPERIMENTAL=enabled"},
			},
			{
				Name: "gcr.io/cloud-builders/docker",
				ID:   "bootstrap-buildx",
				Args: []string{"buildx", "inspect", "--bootstrap"},
				Env:  []string{"DOCKER_CLI_EXPERIMENTAL=enabled"},
			},
			{
				Name: "gcr.io/cloud-builders/docker",
				ID:   "build-image",
				Args: []string{
					"buildx", "build",
					"--platform", platform,
					"--build-arg", "BASE_IMAGE=" + baseImage,
					"-t", outputImage,
					"-f", "Dockerfile",
					"--push", ".",
				},
				Env: []string{"DOCKER_CLI_EXPERIMENTAL=enabled"},
			},
		},
		Options: cloudBuildOptions{
			DynamicSubstitutions: true,
			MachineType:          "E2_HIGHCPU_8",
		},
		Timeout: "1200s",
	}

	cbYAML, err := yaml.Marshal(&cbConfig)
	if err != nil {
		return fmt.Errorf("failed to marshal cloudbuild config: %w", err)
	}

	tmpFile, err := os.CreateTemp("", "scion-cloudbuild-*.yaml")
	if err != nil {
		return fmt.Errorf("failed to create temp cloudbuild config: %w", err)
	}
	defer func() { _ = os.Remove(tmpFile.Name()) }()

	if _, err := tmpFile.Write(cbYAML); err != nil {
		_ = tmpFile.Close()
		return fmt.Errorf("failed to write cloudbuild config: %w", err)
	}
	_ = tmpFile.Close()

	if buildDryRun {
		fmt.Printf("gcloud builds submit --project %s --config %s %s\n", gcpProject, tmpFile.Name(), hcDir.Path)
		fmt.Printf("\n# cloudbuild.yaml contents:\n%s", cbYAML)
		return nil
	}

	fmt.Printf("Submitting Cloud Build in project %s...\n", gcpProject)
	fmt.Printf("Output image: %s\n", outputImage)

	gcloudCmd := exec.CommandContext(cmd.Context(), "gcloud", "builds", "submit",
		"--project", gcpProject,
		"--config", tmpFile.Name(),
		hcDir.Path)
	gcloudCmd.Stdout = os.Stdout
	gcloudCmd.Stderr = os.Stderr
	if err := gcloudCmd.Run(); err != nil {
		return fmt.Errorf("cloud Build failed: %w", err)
	}

	syncBuildToHub(harnessConfigName, hcDir)

	return nil
}

// resolveGCPProject returns the GCP project from settings or gcloud config.
func resolveGCPProject(settings *config.VersionedSettings) string {
	if settings != nil && settings.Server != nil && settings.Server.Secrets != nil && settings.Server.Secrets.GCPProjectID != "" {
		return settings.Server.Secrets.GCPProjectID
	}
	out, err := exec.Command("gcloud", "config", "get-value", "project").Output()
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(out))
}

// syncBuildToHub syncs the harness config to Hub after a build without
// modifying the image field in config.yaml. The image field is a stable
// reference; two-phase resolution at agent start prefers local images.
func syncBuildToHub(harnessConfigName string, hcDir *config.HarnessConfigDir) {
	hubCtx, hubErr := requireHubForUpload(projectPath)
	if errors.Is(hubErr, errHubNotConfigured) {
		// No hub configured: the image is built locally and there is
		// nothing to sync it to.
		return
	}
	if hubErr != nil {
		fmt.Printf("Warning: could not sync to Hub: %v\n", hubErr)
		fmt.Println("Run 'scion harness-config push " + harnessConfigName + "' to sync manually.")
	} else {
		if err := syncHarnessConfigToHub(hubCtx, harnessConfigName, hcDir.Path, "global", "", hcDir.Config.Harness, ""); err != nil {
			fmt.Printf("Warning: failed to sync to Hub: %v\n", err)
			fmt.Println("Run 'scion harness-config push " + harnessConfigName + "' to sync manually.")
		}
	}
}

func init() {
	rootCmd.AddCommand(buildCmd)
	buildCmd.Flags().StringVar(&buildTag, "tag", "latest", "Image tag")
	buildCmd.Flags().StringVar(&buildBaseImage, "base-image", "", "Override the base image (skips image_registry resolution)")
	buildCmd.Flags().BoolVar(&buildPush, "push", false, "Push built image to image_registry after building")
	buildCmd.Flags().StringVar(&buildPlatform, "platform", "", "Target platform (default: current architecture)")
	buildCmd.Flags().BoolVar(&buildDryRun, "dry-run", false, "Show the docker build command without executing")
	buildCmd.Flags().StringVar(&buildBuilder, "builder", "local", "Build backend: local or cloud-build")
}

FILE:cmd/build_context.go
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

FILE:cmd/build_context_test.go
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

FILE:instruccion
Cold-bundle de la tarea task-fase-0-ir-scion-build-pasa-el-contexto-por-stdin-el-docker-snap-no-lee-scion: con el TaskDoc, los rituales enrutados por el Board, las pills ligadas, los átomos ligados y los archivos que el TaskDoc nombra, reformula el encargo, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

Sección de validación del TaskDoc:
- cd scion && go test ./cmd -run 'TestLocalBuildArgs|TestWriteBuildContextTar' -count=1
- scion build <harness-config> --dry-run (binario del fork) imprime 'tar -C <dir> -cf - . | docker build ... -'
- scion build <harness-config> con docker snap termina con rc 0 y la imagen aparece en docker images

