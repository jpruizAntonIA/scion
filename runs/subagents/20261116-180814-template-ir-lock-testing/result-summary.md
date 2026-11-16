# Resultado del tester: validación 4 (lock)

- Tarea: task-fase-0-ir-template-del-ejecutor-de-ir-con-tmp-en-ram-lock-de-tests-compartido-y-tope-de-memoria
- Rol: tester (deskops-tester), run deskops-t-746aca240a1f, subagente local (no Scion)
- Alcance: solo la validación 4 (las 1 a 3 las pasó el tester anterior en runs/subagents/20261116-180814-template-ir-testing)
- Imagen: ghcr.io/jpruizantonia/scion-claude:f6e623c69 (entrypoint `sciontool init --`, cmd `bash`, user root)
- Evidencia: `validation.log` (comandos con su rc y marcas de tiempo) y `v4.sh` (el script que se ejecutó)

## Veredicto: PASS

| Caso | Comando (contenedor) | Esperado | Obtenido |
|---|---|---|---|
| El host sostiene el lock (holder propio `flock -w 3600 ... sleep 40`, 19:34:36Z; `flock -n` en el host da rc=1) | `docker run --rm --user 1001:1001 -v /dev/shm:/dev/shm --entrypoint bash IMG -c 'flock -n /dev/shm/sldb1-tests.lock true; echo rc=$?'` | rc=1 | rc=1 |
| Ídem | `docker run --rm -e SCION_HOST_UID=1001 -e SCION_HOST_GID=1001 -v /dev/shm:/dev/shm IMG bash -c 'id; flock -n ...'` (entrypoint por defecto) | rc=1 | uid=1001(scion), rc=1 |
| El host sostiene el lock (holder de otra suite del host, PID 2338604, 19:09:17Z) | los mismos dos comandos | rc=1 | rc=1 / rc=1 |
| Lock libre (`flock -n` en el host da rc=0, 19:36:05Z) | `--user 1001:1001` | rc=0 | rc=0 |
| Ídem | `SCION_HOST_UID/GID=1001` | rc=0 | uid=1001(scion), rc=0 |
| Control como root (no es la condición que se prueba) | sin `--user` y con `--entrypoint bash` | rc=66 | `Permission denied`, rc=66, tanto con el lock libre como tomado |

## Hallazgos

- El remapeo `SCION_HOST_UID` de sciontool funciona con la imagen: `id` dentro del contenedor muestra uid=1001. El log de sciontool dice "Child exited ... (uid=0, gid=0)", pero esa línea es solo cosmética.
- El gid del host es 1003 (robocop), no 1001. La prueba usa 1001:1001, como dice el contrato. Igual pasa, porque el lock tiene permisos 0644 y su dueño es el uid 1001, así que el gid no importa.
- Se confirma el rc 66 como root por fs.protected_regular=2. No bloquea, porque el agente scion corre remapeado al uid del host.
- Hubo contención: tres suites del host tenían el lock tomado o en cola. Una de ellas (`sldb stores build --check`, PID 2338604) lo sostuvo más de 1 h 46 min. Mi holder lo consiguió unos 56 min después de ponerse en cola y lo sostuvo 40 s. Ninguna suite se vio afectada.
- Limpieza: no borré ni recreé el archivo del lock, no dejé nada en /dev/shm y el `held.marker` temporal del run_dir quedó eliminado.
- No hay pruebas faltantes ni obsoletas para esta validación. Sin seguimientos pendientes.
