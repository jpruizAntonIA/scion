## REFORMULACION

El nodo debe modificar `hooks/pre-start-deskops.sh` (repo SLDB_1, workspace `desk`) para que, en vez de copiar sldb y deskops a `/tmp` con `mktemp`+`tar`, los instale editables desde `$SCION_WORKSPACE/sldb` y `$SCION_WORKSPACE/deskops` (por defecto `/workspace`) mediante `uv tool install --editable`; además sldb debe quedar editable dentro del venv de deskops vía `--with-editable`. Mantiene uv propio, Python 3.13, salida no cero si falta herramienta y PATH en `.profile`/`.bashrc`. Fuera de alcance: registrar el hook en el hub (fase 1), imágenes y código de sldb/deskops. Resultado observable: en contenedor con workspace en `/workspace`, rc 0, `deskops --help`/`sldb --help` funcionan y los módulos resuelven a `/workspace`.

## AMBIGUEDADES

1. "desde $SCION_WORKSPACE/sldb y $SCION_WORKSPACE/deskops (por defecto /workspace)": no indica cómo resolver el fallback si la variable está vacía o ausente; obligaría a inventar la lógica de expansión.
2. "`--python $PYTHON_SPEC`": no se define `PYTHON_SPEC`; obligaría a inventar su valor o procedencia.
3. "salida no cero si falta una herramienta": no enumera qué herramientas; obligaría a decidir si incluye uv, python o ambas.
4. "Los *.egg-info que escribe setuptools junto a las fuentes están ignorados por git en sldb y deskops": no aclara si es un hecho a verificar o una acción a realizar; obligaría a inventar si el ejecutor debe tocar `.gitignore`.

## DRY-RUN

Lecturas: `hooks/pre-start-deskops.sh` y, si aplica, `.gitignore` de sldb/deskops. Cambios previstos: sustituir el bloque `mktemp`+`tar` por dos `uv tool install --quiet --python ... --reinstall --editable`, el de deskops con `--with-editable` hacia sldb; ajustar comentarios. Dependencias: uv, Python 3.13, `SCION_WORKSPACE`, acceso a paquetes. Validaciones futuras: `bash -n` y `docker run` con imagen claude del fork y workspace montado, comprobando rc 0, `--help` y `__file__` bajo `/workspace`.

## FUTURO

Registro del hook en el hub (fase 1) y provisión del hub del fork; decisión humana sobre `PYTHON_SPEC` y el fallback de `SCION_WORKSPACE`; ejecución real de la validación docker. No son ambigüedades del nodo.
