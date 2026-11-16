# Propuesta: endpoint del hub de producción para ejecutores pi en red bridge

Fecha: 2026-11-16. Ejecutor deskops-e-20f39328c207. Evidencia: `validation.log`, `probe-red.txt` de este run.

## Conclusión corta

**La decisión tomada (agregar `--host 172.17.0.1` a los argumentos del hub de producción) no se puede aplicar tal cual:
el hub no arranca.** El binario de producción (`~/.local/bin/scion`, `scion dev (commit f6e623c6)`) es el mismo
commit que el fork del lab y trae los mismos dos guards. El lab los encontró uno tras otro:

1. Con `--dev-auth=true` (lo que usa producción) y `--host 172.17.0.1`, el arranque falla con
   `Error: dev auth cannot be enabled when the server is bound to a non-loopback address (172.17.0.1). Dev auth signs browsers in as admin and must only be used on localhost.`
   (`cmd/server_web_base_url.go:160-170` `webStartupPreflight`; también `cmd/server_foreground.go:3811` y `pkg/hub/web.go:710`).
2. Con `--dev-auth=false`, falla con
   `Error: refusing to start the web server: its base URL http://localhost:18080 (from default) is not https, and it listens on 172.17.0.1:18080, which is not a loopback address`.
   El hub pide entonces una base URL https (`--base-url`, `SCION_SERVER_BASE_URL` o `server.hub.public_url`).

Además el probe muestra que **ufw está activo con `DEFAULT_INPUT_POLICY="DROP"`** (`/etc/default/ufw`). Desde un
contenedor bridge, `172.17.0.1:8000` hace timeout aunque escucha en `0.0.0.0:8000`, y lo mismo el curl a
`172.17.0.1:18080`: el paquete se descarta, no se rechaza. Por eso un hub en `172.17.0.1` tampoco sería alcanzable
desde el bridge sin una regla `allow` de ufw. Esa regla es de JP (sudo).

Para que la decisión funcione hacen falta las tres cosas siguientes, y ninguna es de esta tarea:
(a) dejar `--dev-auth` o cambiar el código Go;
(b) tener una base URL https, o cambiar el código Go;
(c) agregar una regla ufw que abra el puerto del hub solo en docker0.

## Cómo decide scion la red del agente (inventario de cmd/ y pkg/)

- `pkg/runtime/common.go:2098` `ResolveHostNetworking`: el agente va con `--network host` en tres casos:
  - `SCION_FORCE_HOST_NETWORK` está definido (cualquier runtime);
  - el `SCION_HUB_ENDPOINT` del agente contiene `host.docker.internal`;
  - el host del endpoint es `localhost`, `127.0.0.1` o `::1`.

  En cualquier otro caso el agente va en bridge (`""`). Se aplica en `pkg/agent/run.go:1632` y `pkg/runtime/common.go:413`.
- `cmd/server_container_hub.go:148` `computeContainerHubEndpoint` decide el endpoint que reciben los agentes colocados:
  - `runtime_broker.container_hub_endpoint` configurado: gana.
  - URL pública no loopback (`--base-url`, `public_url`): bridge con esa URL.
  - URL pública derivada de IAP: bridge con `http://scion-hub.internal:<puerto>` mapeado a host-gateway.
  - En otro caso: `containerBridgeEndpoint`, que pone `host.docker.internal` (`cmd/server_helpers.go:84`), y eso
    vuelve a red host con el WARNING "no public domain configured…".
- Hoy producción no tiene `--host` ni base URL, así que su endpoint es loopback. Por eso sus ejecutores corren en
  red host, que es lo que vio el piloto de mepu.
- `pkg/sciontool/metadata/server.go:213` desactiva la intercepción de metadata cuando `NetworkMode == host`.

## Opciones

### A. `--host 172.17.0.1` (la decisión tomada): NO aplicable sin cambios previos

- Con los argumentos actuales el hub no arranca (guard 1). Si se aplicara a ciegas, producción queda caída hasta la
  vuelta atrás.
- Riesgo si se desactivaran los guards (cambio Go, fuera de alcance): `--dev-auth` da admin a cualquier navegador.
  En `172.17.0.1:8080` lo alcanzaría todo contenedor de la máquina, incluidos los propios agentes, que podrían
  escalar a admin del hub.
- Comandos, solo como referencia (hoy fallan en el arranque):

  ```sh
  # aplicación
  ~/.local/bin/scion server stop
  ~/.local/bin/scion server start --enable-hub=true --enable-runtime-broker=true --enable-web=true \
    --dev-auth=true --auto-provide=true \
    --web-assets-dir=/home/robocop/scion-build/web-v0.2.21/web/dist/client --host 172.17.0.1
  # (o agregar "--host","172.17.0.1" a ~/.scion/server-args.json si el servicio arranca desde ese archivo)
  # vuelta atrás: los argumentos originales
  ~/.local/bin/scion server stop
  ~/.local/bin/scion server start --enable-hub=true --enable-runtime-broker=true --enable-web=true \
    --dev-auth=true --auto-provide=true \
    --web-assets-dir=/home/robocop/scion-build/web-v0.2.21/web/dist/client
  ```

### B. `--host 172.17.0.1 --dev-auth=false --base-url https://<nombre>` con TLS delante

- Cumple los dos guards, pero hace falta un frente TLS (Caddy u otro) y un modo de auth real (OAuth o proxy) para
  el CLI y la web. Hoy el CLI del host usa dev-auth. Es un cambio de despliegue grande y queda como decisión de JP.
- Requiere igual la regla ufw de la opción C.

### C. Regla de firewall (ya con ufw activo)

ufw ya aísla los servicios del host del bridge: `172.17.0.1:15432` y `:8000` no responden desde el bridge.
**No hace falta una regla nueva para cerrarlos.** Si el hub llega a escuchar en 172.17.0.1, para abrir SOLO el hub y
solo desde docker0 (para JP, con sudo):

```sh
sudo ufw allow in on docker0 to 172.17.0.1 port 8080 proto tcp comment 'scion hub para agentes bridge'
# vuelta atrás
sudo ufw delete allow in on docker0 to 172.17.0.1 port 8080 proto tcp
```

Si se quiere el cierre explícito de :8000 y :15432 aunque cambie la política por defecto (opcional; hoy ya caen en
DROP):

```sh
sudo ufw deny in on docker0 to any port 8000 proto tcp
sudo ufw deny in on docker0 to any port 15432 proto tcp
```

No pude leer las reglas actuales de ufw (`/etc/ufw/user.rules` y `ufw status` exigen root). JP debe confirmar que no
haya ya un `allow` sobre docker0.

### D. Recomendación

No aplicar A. La vía sin cambios de código es B + C, una decisión de despliegue de JP. Si se prefiere mantener
dev-auth, hace falta un cambio Go: permitir dev-auth en un host no loopback restringido a la interfaz del bridge, o
dar a los agentes un listener de solo Hub API (sin web ni dev-auth) en 172.17.0.1. Eso es una propuesta para una
tarea de código aparte.

## Lo que no se pudo validar en el lab

- No se ejecutó ningún agente lanzado por scion en bridge, así que falta la validación de NetworkMode. El probe de
  `probe-red.txt` es de respaldo (`docker run --rm --network bridge`).
- La respuesta del hub de lab desde el bridge da `000`, porque el hub no arrancó y además ufw descartaría el tráfico.
