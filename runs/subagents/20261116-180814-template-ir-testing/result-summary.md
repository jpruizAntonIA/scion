# result-summary: tester deskops-t-8bfe438ea7fe

- Tarea: task-fase-0-ir-template-del-ejecutor-de-ir-con-tmp-en-ram-lock-de-tests-compartido-y-tope-de-memoria
- Rol: tester (role-deskops-tester), intento 1, subagente local (no Scion)
- Run dir: runs/subagents/20261116-180814-template-ir-testing. Comandos y rc en validation.log.

## Estado del trabajo
- deskops /mnt/ssd/herramientas/deskops HEAD 4a8b4b97 (limpio): 4a7707a5, 4c745c18 y 881e177a son ancestros (rc 0).
- IR: 5b8ce32 es ancestro de HEAD 3ec37f2 (rc 0). `deskops list roles` -> role-ir-executor; `deskops list runtime-profiles` -> runtime-claude-en-scion (kind claude, binary claude). Salidas en show-role.txt y show-runtime-profile.txt. El rol tiene las reglas del brief en el cuerpo.
- Nota: `deskops show role ir-executor` da rc 1 (el name no sirve como selector); `show role role-ir-executor` da rc 0.
- .bootstrap/ir-scion-context.json: todas las claves coinciden con el contrato.
- IR/.scion/templates/ir-executor/scion-agent.yaml tiene TMPDIR=/dev/shm, el volumen /dev/shm y resources.limits memory 6Gi / cpu 2.

## Validaciones
Python usado: `uv run --no-project --with pytest --with-editable /mnt/ssd/herramientas/deskops --with-editable /mnt/ssd/herramientas/sldb python -m pytest -q -p no:cacheprovider`. El python de la tool de deskops no tiene pytest. Corrí desde /mnt/ssd/herramientas/deskops con TMPDIR=/dev/shm, un archivo a la vez.

| # | validación | resultado | veredicto |
|---|---|---|---|
| a1 | tests/test_scion_runtime.py | 35 passed (45 s) | PASS |
| a2 | tests/test_role_runtime_artifacts.py | 3 passed (51 s) | PASS |
| a3 | tests/test_command_registry.py | 3 passed (11 s) | PASS |
| a4 | tests/test_output_goldens.py -k test_help_goldens | 1 passed, 6 deselected (451 s) | PASS |
| b | fsync en el contenedor scion-claude:f6e623c69, --memory 6g, -v /dev/shm, TMPDIR=/dev/shm, cwd sldb/ | tests/store/test_io_atomic_write.py: 2 passed in **0.53 s** según pytest (2.18 s de pared con el arranque del contenedor) | PASS |
| c | lock compartido | NO CORRIDO COMO PIDE EL CONTRATO: otra suite del host tuvo /dev/shm/sldb1-tests.lock tomado todo el tiempo, así que no pude sostenerlo yo ni probar el caso libre (rc 0). Pruebas parciales con el lock en manos de esa suite: ver abajo | INCOMPLETO |

En b, la imagen no trae pytest. Usé su python3 3.13.5 con PYTHONPATH=sldb/.venv/lib/python3.13/site-packages:sldb/src y PYTHONDONTWRITEBYTECODE=1. Esa corrida dejó /dev/shm/pytest-of-root (de root, creado por mí a las 15:22:05) y lo borré.

### Hallazgo en c (bloquea c tal como está escrita)
El host tiene fs.protected_regular=2 y el lock es de robocop (1001). Por eso `flock -n /dev/shm/sldb1-tests.lock true` dentro del contenedor, corriendo como root (docker run sin usuario, sciontool en modo local), da **rc 66 (Permission denied)**, no rc 1: flock abre con O_CREAT y protected_regular lo niega aunque seas root.
- Con --user 1001:1001: rc 1 (correcto).
- Como root abriendo sin O_CREAT (`exec 9<lock; flock -n 9`): rc 1.
- Con SCION_HOST_UID/GID=1001 (sciontool remapea al usuario scion a 1001): rc 1.
Así que, si el broker pasa SCION_HOST_UID, el agente comparte bien el lock. Pero el comando del contrato con docker run a secas no da rc 1. Además, si el lock no existe y lo crea un contenedor como root, después el host no podrá abrirlo con O_CREAT.

## Global
**FAIL / INCOMPLETO**: a y b pasan; c sigue pendiente. Falta repetir c con el lock libre, el host sosteniéndolo con `flock ... sleep 30` y el contenedor corriendo con el uid del host (SCION_HOST_UID=1001 o --user 1001). Hay que decidir si el contrato debe exigir correr como el uid del host.

## Tests que pasaron (para --test)
- deskops:tests/test_scion_runtime.py
- deskops:tests/test_role_runtime_artifacts.py
- deskops:tests/test_command_registry.py
- deskops:tests/test_output_goldens.py (solo -k test_help_goldens)
