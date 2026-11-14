## REFORMULACION

Encargo ejecutable (task.code, no agregado): crear en el repo scion (rama `wt/pi-harness`) el bundle `harnesses/pi/` para que scion instale, construya imagen, aprovisione y ejecute `pi` (@mariozechner/pi-coding-agent) con DeepSeek Flash por defecto, incluyendo parada y reanudación de sesión. Resultado: ocho ficheros (`config.yaml`, `Dockerfile`, `provision.py`, `provision_test.py`, `scion_harness.py` vendido byte-idéntico, `capture_auth.py`, `home/.bashrc`, `README.md`), patrón de `harnesses/opencode/` y `harnesses/authoring-guide.md`. Límites: solo `harnesses/pi/`; fuera Go del host, otros harnesses, el `scion_harness.py` compartido, push y credenciales reales; prohibido copiar `~/.pi/agent/auth.json` o `secrets.env` al repo/imagen.

## AMBIGUEDADES

1. "npm install -g @mariozechner/pi-coding-agent" — sin versión fijada; obliga a inventar el pin para reproducibilidad.
2. "ensure node >= 20.6 (fail the build if older)" — no dice si instalar Node cuando `BASE_IMAGE` no lo trae; obliga a inventar el método.
3. "models deepseek-flash and deepseek-v4-pro" — no confirma que sean identificadores válidos de la API; obliga a asumirlos.
4. "an auth-file type targeting .pi/agent/auth.json" — formato de esquema y ruta del fichero "scion-staged" no especificados; obliga a inventar ambos.
5. "Merge, do not clobber, pre-existing user keys in settings.json" — no define merge superficial vs profundo; obliga a elegir.
6. "honest capabilities (mark unsupported features \"no\" with a reason)" — no enumera qué features ni el texto de razón; obliga a inventariarlas.
7. "capture_auth.py shim" — comportamiento no descrito; obliga a inventar su contrato.
8. "TMPDIR=/dev/shm ... MemoryMax=2G" vs "coordinator runs it only when IO pressure allows" — criterio de IO no cuantificado; obliga a inventar el umbral.
9. "stop + resume continues the session" — no define la observación concreta; obliga a inventar el criterio de éxito.

## DRY-RUN

Lecturas: TaskDoc, `harnesses/opencode/*`, `harnesses/authoring-guide.md`, `harnesses/scion_harness.py`. Cambios: crear los ocho ficheros listados. Dependencias: Node ≥20.6/npm, CLI scion, clave DeepSeek (para smoke). Validaciones futuras: install de esquema, `provision_test.py` bajo systemd-run, `cmp` del lib, build de imagen, smoke en `~/lab-scion`, grep de secretos.

## FUTURO

Humano (JP): registrar la clave DeepSeek en scion y aprobar ejecución del build bajo presión IO. Otro nodo/coordinador: ejecutar build y smoke; commit local en `wt/pi-harness`.
