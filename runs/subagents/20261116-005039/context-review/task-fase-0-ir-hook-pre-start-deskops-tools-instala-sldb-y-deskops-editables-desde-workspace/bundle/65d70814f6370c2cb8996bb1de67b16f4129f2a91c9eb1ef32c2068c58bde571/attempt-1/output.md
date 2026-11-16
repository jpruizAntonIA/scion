## REFORMULACION

**Propósito:** que el hook pre-start del fork scion monte las herramientas del ejecutor en modo editable, de forma que los cambios en `sldb` y `deskops` dentro del workspace se reflejen sin reinstalar ni reiniciar. **Resultado:** `hooks/pre-start-deskops.sh` instala ambos paquetes con `uv tool install --editable` desde `$SCION_WORKSPACE/sldb` y `$SCION_WORKSPACE/deskops` (por defecto `/workspace`), incluyendo sldb editable en el venv de deskops mediante `--with-editable`; conserva comprobaciones de `pyproject.toml`, instalación de uv, verificación de ejecutables y PATH. **Repo:** fork scion (el archivo vive en `hooks/`). **Límites:** no toca `.gitignore`, imágenes ni código de sldb/deskops; registrar el hook en el hub queda para fase 1. Es una tarea ejecutable (`task.code`), no un agregado.

## AMBIGUEDADES

1. «Reemplazar el bloque de copias (mktemp + tar) por dos `uv tool install…`»: el archivo aportado ya contiene exactamente esas instalaciones editables y ningún bloque `mktemp`/`tar`. Obligaría a inventar si la tarea ya está aplicada o qué diff se espera.
2. «docker run (imagen claude del fork, workspace en /workspace) ejecuta el hook»: no se da nombre/tag de imagen ni comando concreto. Obligaría a inventar el identificador y los argumentos del contenedor.
3. «python del venv de deskops imprime `deskops.__file__`»: no se indica ruta ni cómo localizar ese venv. Obligaría a inventar el comando de descubrimiento.

## DRY-RUN

**Lecturas:** el hook, ambos `pyproject.toml`, y `git check-ignore` sobre patrones `*.egg-info` en sldb/deskops. **Cambios previstos:** sustituir el bloque de copias por las dos instalaciones editables (una con `--with-editable`) y ajustar comentarios; conservar uv, validaciones de rutas/ejecutables y PATH. **Dependencias:** uv/curl/wget, Python 3.13, imagen docker del fork. **Validaciones futuras:** `bash -n`, ejecución del hook en contenedor con rc 0, `deskops --help`/`sldb --help`, y `__file__` bajo `/workspace/deskops` y `/workspace/sldb/src`. Sin ejecutar nada.

## FUTURO

Fase 1 registra el hook en el hub. Un humano/CI aporta la imagen y ejecuta la validación docker; el ritual de closeout actualiza el board y prepara el commit tras pasar las validaciones.
