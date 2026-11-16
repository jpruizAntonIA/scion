## REFORMULACION

Propósito: que JP decida dos cosas de la fase 0 de IR: mover la raíz de Docker al SSD (`/mnt/ssd/docker`) y sustituir Docker snap por Docker CE de apt. Resultado: decisión registrada, apoyada en la recomendación y comandos exactos del informe `reports/scion-piloto-ir-20261115.md`. Repo: `SLDB_1/scion`. Límites: solo decisión y registro; queda fuera ejecutar el cambio sin JP. Es un nodo de decisión no ejecutable: no tiene hijos ni átomos; no hay recorrido de agregado.

## AMBIGUEDADES

1. “si mueve la raíz de docker al SSD ... y si cambia el docker snap por docker-ce” no aclara si son una decisión conjunta o dos independientes. Obligaría a inventar el formato de disposición (una sola respuesta o dos).
2. “con la recomendación y los comandos exactos del informe” remite a un informe cuyo contenido no está en el input. Obligaría a inventar recomendación y comandos.
3. “deskops review status de esta tarea muestra la disposición de JP” no define dónde ni cómo se registra la disposición. Obligaría a inventar el mecanismo de registro.
4. “El docker snap además no lee directorios ocultos de $HOME” no indica si es motivación o restricción operativa relevante. Obligaría a inventar su peso en la decisión.

## DRY-RUN

Lecturas hipotéticas: TaskDoc, informe citado y estado de review en deskops. Cambios previstos por un ejecutor futuro: ninguno técnico; solo consignar la decisión de JP. Dependencias: JP y el informe. Validaciones futuras: que deskops muestre la disposición y que la decisión cubra mover raíz y cambiar o no Docker snap. Sin ejecutar nada.

## FUTURO

JP produce la decisión. Otro nodo, si procede, ejecutará la opción elegida; un humano valida el registro.
