## REFORMULACION
Encargo ejecutable (no agregado): producir, para el piloto en IR, un binario del fork de scion y tres imágenes Docker construidos desde el mismo commit C, sin usar `ghcr.io/homebrew-scion`.

- **Propósito:** sustituir la release v0.2.21 de Homebrew por artefactos del fork que soporten bloques ready/delivery y hooks.
- **Resultado:** binario instalado en `/mnt/ssd/herramientas/scion-fork/<sha>/scion` cuyo `scion version` muestra C; imágenes locales `core-base`, `scion-base` y `scion-claude` en `ghcr.io/jpruizantonia` con tags `:latest` y `:<sha corto de C>`; versión anotada en `reports/scion-piloto-ir-20261115.md`.
- **Repo:** fork de scion; el input no indica URL ni ruta de checkout.
- **Límites:** compilar con `make build` y cachés en `/mnt/ssd/cache`; no pisar `~/.local/bin/scion`; construir de a una imagen; no hacer push, no reiniciar el hub, no tocar otros harnesses ni el Docker de la máquina. La activación y `image_registry` son pasos de JP.

## AMBIGUEDADES
1. «compilado en el commit C» / «tag <sha>»: no se da el SHA concreto; obliga a inventar C.
2. «make build»: no se especifica ruta del checkout del fork ni cómo obtener/verificar C; obliga a inventar origen y checkout.
3. «build-images.sh --registry ghcr.io/jpruizantonia --target core-base|scion-base|scion-claude»: no queda claro si `--target` acepta esos valores o es sintaxis abreviada; obliga a inventar la invocación exacta.
4. «La versión queda anotada en reports/...»: no se define formato, contenido ni si el informe está en scope; obliga a inventar la edición.
5. «quedan como comandos exactos en el informe»: no se dan los comandos de JP; obliga a inventarlos.
6. «ninguna referencia de la configuración nueva apunta a ghcr.io/homebrew-scion»: la configuración la cambia JP y no se indica qué archivo o comprobación usar; obliga a inventar el criterio de validación.

## DRY-RUN
Sin ejecutar: leer TaskDoc, checkout del fork en C, Makefile y `image-build/scripts/build-images.sh`. Previsto: construir binario con cachés; instalar copia versionada; construir secuencialmente las tres imágenes con registry y tags; editar el informe con versión y comandos para JP. Dependencias: C disponible, Go, Docker, cachés, script y nombre de registry. Validaciones futuras: `scion version` muestra C; `docker images` lista las tres imágenes con tag corto; revisar que la configuración nueva no referencie Homebrew. No push, reinicio ni cambio de settings.

## FUTURO
JP reemplaza `~/.local/bin/scion`, reinicia el hub en `:8080`, fija `image_registry` y valida ausencia de `ghcr.io/homebrew-scion`. Otro nodo/humano debe aportar el SHA C, la ruta del fork y revisar el informe.
