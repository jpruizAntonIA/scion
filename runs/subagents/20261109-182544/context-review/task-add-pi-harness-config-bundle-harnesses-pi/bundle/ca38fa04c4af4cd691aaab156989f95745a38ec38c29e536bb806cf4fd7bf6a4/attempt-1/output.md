REFORMULACION
Propósito: crear el bundle harness-config `harnesses/pi/` para que scion lo instale, construya imagen, aprovisione y ejecute pi (`@mariozechner/pi-coding-agent` 0.73.1) con DeepSeek Flash por defecto, incluyendo stop + resume de sesión. Resultado: los ocho archivos de `files`, siguiendo el patrón de `harnesses/opencode/` y `authoring-guide.md`. Repo: scion-wt-pi-harness, rama wt/pi-harness. Es una tarea `task.code` ejecutable, no un agregado. Límites: solo `harnesses/pi/`; fuera Go host, otros harnesses, el `scion_harness.py` compartido, cualquier push y credenciales reales; nunca copiar auth.json/secrets.env ni claves.

AMBIGUEDADES
1. "declare the same keys opencode declares": el input no enumera esas claves ni aporta `harnesses/opencode/`; obligaría a inventar la lista de capacidades.
2. "use whatever field value the settings-v1 schema accepts": el esquema no está en el input; obligaría a inventar nombre y tipo del campo auth-file.
3. "the same npmrc secret mount + cache clean as opencode": sin el Dockerfile de opencode habría que inventar la sintaxis del mount y la limpieza.
4. "the same non-secret fields the host desks use": la configuración de los desks no se aporta; obligaría a inventar campos de `models.json`.
5. "settings.json is a shallow top-level merge (scion sets defaultProvider/defaultModel, every other existing key preserved)": no aclara si un defaultProvider/defaultModel previo se sobrescribe; obligaría a decidir la política de colisión.
6. "mark each yes/partial/no from what pi 0.73.1 actually supports (pi --help)": no hay salida de `pi --help`; obligaría a inventar el soporte real.

DRY-RUN
Lecturas: TaskDoc, rituales enrutados (phase/execution/testing/closeout), `authoring-guide.md`, `harnesses/opencode/*`, `harnesses/scion_harness.py` y el estado de `harnesses/pi/`. Cambios previstos: crear los ocho archivos. Dependencias: CLI/esquema de scion, acceso npm, `BASE_IMAGE` scion-base y clave DeepSeek para el smoke. Validaciones futuras: las seis listadas en Validación.

FUTURO
El coordinador ejecuta el build solo con IO avg60 < 30; JP registra `DEEPSEEK_API_KEY` en scion; el smoke y el resume los corre el coordinador, no el ejecutor.
