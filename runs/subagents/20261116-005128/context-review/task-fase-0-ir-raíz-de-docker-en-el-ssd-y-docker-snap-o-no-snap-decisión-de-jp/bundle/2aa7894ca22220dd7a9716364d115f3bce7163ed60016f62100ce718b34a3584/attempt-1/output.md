## REFORMULACION

Propósito: obtener de JP dos decisiones independientes de fase 0 IR: (1) mover la raíz de Docker del HDD (`/var/snap/docker/common/var-lib-docker`) al SSD (`/mnt/ssd/docker`, `data-root` en `daemon.json`); (2) mantener docker snap o pasar a docker-ce de apt. Resultado: disposición registrada de JP cuya razón declare qué eligió en (1) y en (2). Entorno: `/mnt/ssd/proyectos/SLDB_1/scion`; informe fuente `/mnt/ssd/proyectos/SLDB_1/reports/scion-piloto-ir-20261115.md`, sección Fase 0. Límites: no ejecutar cambios sin JP; el worker solo registra owner; que el snap no lea ocultos de `$HOME` ya no bloquea.

Nodo no ejecutable: es una decisión hoja (`depends_on: []`, `atoms: []`), sin hijos. El “hijo” operativo es la disposición de JP.

## AMBIGUEDADES

1. “dos decisiones independientes, cada una con su respuesta” frente a “deskops review status de esta tarea muestra la disposición de JP”: no fija si una disposición parcial cierra; obligaría a inventar el criterio de completitud.
2. “el worker registra JP como owner”: no identifica qué worker/agente; obligaría a inventar el ejecutor.
3. “deskops review dispose sobre el recibo de esta tarea”: no define si “recibo” es el registro owner o la tarea; obligaría a inventar el objeto exacto del dispose.
4. “tarea hermana”: no se nombra; obligaría a inventar su identificador.
5. “con la recomendación y los comandos exactos del informe”: no declara qué hacer si el informe falta o no contiene esa sección; obligaría a inventar un fallback.

## DRY-RUN

Lecturas: TaskDoc, rituales enrutados, informe Fase 0. Cambios previstos: ninguno en repo/sistema; solo registros en deskops. Secuencia hipotética: el worker ejecuta `deskops review record --kind owner` sobre esta tarea; JP lee la recomendación; JP ejecuta `deskops review dispose` con razón que mencione (1) y (2). Dependencias: informe disponible, CLI deskops e identidad de JP. Validación futura: `deskops review status` muestra la disposición y su razón cubre ambas decisiones. No hay cadena de hijos que transferir.

## FUTURO

JP decide (1) y (2); el nodo/agente autor del informe entrega recomendación y comandos; la tarea hermana resuelve el paso de contexto por stdin; un humano supervisor confirma el cierre.
