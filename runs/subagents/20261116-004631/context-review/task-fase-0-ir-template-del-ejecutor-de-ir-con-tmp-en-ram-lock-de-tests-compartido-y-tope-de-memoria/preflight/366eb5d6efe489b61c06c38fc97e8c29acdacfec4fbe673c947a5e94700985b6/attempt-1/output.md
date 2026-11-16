## REFORMULACION

El nodo debe preparar la Fase 0 del ejecutor IR de scion: en deskops, añadir `deskops add|edit|list|show role` y `runtime-profile`, y ampliar `deskops runtime template` para que su `--context-file` acepte `memory_limit`, `cpu_limit`, `shared_paths` y `env`, emitiendo `resources.limits`, volúmenes con la misma ruta y env en `scion-agent.yaml`. En el desk de IR, solo vía deskops, crear un RoleDoc claude y un RuntimeProfileDoc claude, generar el template `ir-executor` con TMPDIR=/dev/shm, /dev/shm compartido y tope de memoria, y medir un test de fsync <2 s. Límites: fuera código de IR, lanzamiento de agentes y cambios del Docker de la máquina.

## AMBIGUEDADES

1. «el tope de memoria (31 GB en la máquina, 3-4 agentes como máximo)»: no fija el valor por agente ni `cpu_limit`; obligaría a inventar cifras.
2. «con las reglas del brief dentro del rol»: el brief no consta en el input; obligaría a inventar su contenido.
3. «el test de fsync de sldb»: sin ruta ni nombre; obligaría a inventar qué test ejecutar.
4. «volúmenes con la misma ruta»: no indica opciones de montaje (rw, propagation); obligaría a inventarlas.
5. «anotada en el informe»: sin ruta ni formato; obligaría a inventar el destino.

## DRY-RUN

Lecturas: `models/role.py`, `models/runtime_profile.py`, `doc_access.py`, `cli/model_introspection.py`, `runtime/scion.py`, tests y goldens de help; estructura del desk IR, `.bootstrap/` y el test de fsync de sldb. Cambios previstos: `__artifact__` y registro `ARTIFACT_*`, `_validate_container_keys`, comandos CLI y mapeo de claves a YAML; creación de RoleDoc/RuntimeProfileDoc; generación del template. Dependencias: CLI deskops operativa, imagen del fork y Docker con `/dev/shm`, lock compartido. Validaciones futuras: pytest por archivo con TMPDIR=/dev/shm, goldens de help, inspección del YAML y `docker run` con memoria, volumen y TMPDIR midiendo <2 s.

## FUTURO

La fase 1 consumirá el template para lanzar agentes. Un humano decide los valores exactos de memoria/CPU, el texto del brief, qué test de fsync usar y dónde queda el informe.
