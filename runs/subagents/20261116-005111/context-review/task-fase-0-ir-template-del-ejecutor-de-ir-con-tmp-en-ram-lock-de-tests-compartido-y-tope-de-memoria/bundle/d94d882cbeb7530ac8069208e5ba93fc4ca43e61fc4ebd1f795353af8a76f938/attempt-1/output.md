## REFORMULACION
Encargo: ampliar deskops para crear/gestionar RoleDoc y RuntimeProfileDoc (`add|edit|list|show`), aceptar en `runtime template --context-file` las claves `memory_limit`, `cpu_limit`, `shared_paths`, `env` y emitir resources.limits, volúmenes y env en `scion-agent.yaml`. Con eso, crear en el desk de IR un rol `ir-executor` (kind claude, reglas del brief en el body) y un runtime-profile claude, generar el template con TMPDIR=/dev/shm, /dev/shm compartido y tope de memoria, y medir un test sldb con fsync dentro de contenedor: <2 s. Resultado: cambios deskops con tests/goldens verdes, template IR correcto y sección Fase 0 del informe. Repo: deskops; desk IR solo vía deskops; sldb para medición; `.bootstrap/` y `reports/` de SLDB_1. Límites: fuera código de IR, lanzar agentes scion (fase 1) y cambiar el docker de la máquina.

## AMBIGUEDADES
1. "docker run con --memory=<tope>" frente a "memory_limit 6Gi": no fija el tope de la medición; obligaría a inventar valor.
2. "ghcr.io/jpruizantonia/scion-claude:<C>": tag `C` sin definir; obliga a inventar imagen.
3. "un test real de sldb" y "sldb tests/store/test_io_atomic_write.py": ruta relativa ambigua respecto a `sldb/src`; obliga a inventar ubicación/Comando.
4. "deskops add|edit|list|show role": no define opciones, formato de salida ni goldens; obliga a inventar contrato CLI.
5. "con las reglas del brief dentro del rol": no identifica el brief ni su formato; obliga a inventar fuente y serialización.
6. "lock de tests compartido": solo aparece como regla del rol; no dice cómo se toma/verifica en template o medición; obliga a inventar mecanismo.
7. "role-ir-executor" frente a "add role --name ir-executor": no aclara convención ni carpeta del template; obliga a inventar mapeo.
8. "una suite completa por integración": "integración" no definida; obliga a inventar alcance.

## DRY-RUN
Lecturas: `models/role.py`, `models/runtime_profile.py`, `doc_access.py`, `cli/model_introspection.py`, `runtime/scion.py`, tests y goldens; estado del desk IR; context file en `.bootstrap/`; informe. Cambios previstos: modelos/registro artifact, validación de claves, comandos role/runtime-profile, tests/goldens; crear context JSON, RoleDoc, RuntimeProfileDoc, template; ejecutar contenedor de medición. Dependencias: deskops operativo antes de crear docs/template; imagen disponible; `/dev/shm` compartido. Validaciones futuras: pytest por archivo, goldens de help, yaml con limits/volumen/TMPDIR, medición fsync <2 s.

## FUTURO
Un humano decide tag de imagen y tope exacto; otro nodo ejecuta la medición y redacta el informe; el ritual de fase integra y cierra con commit.
