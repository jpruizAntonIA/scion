REFORMULACION
Propósito: en el repo /mnt/ssd/proyectos/SLDB_1/scion, tras commitear el código de fase 0, compilar el binario del fork en el commit C y construir localmente core-base, scion-base y scion-claude desde ese mismo C con registro ghcr.io/jpruizantonia. Resultado: binario en /mnt/ssd/herramientas/scion-fork/<C>/scion, tres imágenes con tags :latest y :<sha corto>, y sección "Fase 0" en reports/scion-piloto-ir-20261115.md con tabla y comandos literales para JP. Límites: sin push, sin reiniciar hub, sin pisar ~/.local/bin/scion, sin otros harnesses ni cambiar el docker de la máquina.

AMBIGUEDADES
1. "C = git rev-parse --short HEAD en ese momento": no define árbol limpio ni qué hacer si el commit de fase 0 aún no existe; obligaría a inventar una precondición.
2. "los mismos argumentos de ~/.scion/server-args.json": el archivo no está en el bundle; inventaría su contenido.
3. "build-images.sh --help acepta step IDs individuales como target con local-docker": afirmación no verificada; obligaría a inventar un fallback si es falsa.
4. "template generado del ejecutor de IR": no indica ruta ni cómo generarlo; inventaría el artefacto a grepear.
5. "docker images --filter reference=ghcr.io/jpruizantonia/*": el glob sin comillas puede expandirse en shell; no aclara si la validación busca solo :<C> o también :latest.

DRY-RUN
Lecturas: TaskDoc, rituales phase/execution/testing/closeout, git status/rev-parse, build-images.sh --help, docker info e informe existente. Cambios previstos: make build con GOCACHE=/mnt/ssd/cache/go-build y GOMODCACHE=/mnt/ssd/cache/go-mod; install -D a ruta versionada; tres ejecuciones secuenciales de build-images.sh; edición de la sección del informe. Dependencias: commit C ya creado, docker local operativo y caches. Validaciones futuras: scion version contiene el commit C; docker images lista las tres imágenes con tag C; grep sin homebrew-scion en template y comandos.

FUTURO
JP instala el binario en ~/.local/bin/scion, reinicia el hub en :8080 con server-args.json y fija image_registry en ~/.scion/settings.yaml; decide si publica las imágenes (push queda fuera). El nodo de cierre integra y valida el conjunto.
