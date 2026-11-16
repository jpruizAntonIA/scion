#!/usr/bin/env bash
# Validación 4 (lock) — tester deskops-t-746aca240a1f
R=/mnt/ssd/proyectos/SLDB_1/scion/runs/subagents/20261116-180814-template-ir-lock-testing
L=/dev/shm/sldb1-tests.lock
IMG=ghcr.io/jpruizantonia/scion-claude:f6e623c69
LOG=$R/validation.log
M=$R/held.marker
log(){ echo "[$(date -u +%FT%TZ)] $*" >> $LOG; }
run(){ log "CMD: $*"; out=$("$@" 2>&1); rc=$?; log "OUT: $(echo "$out" | tail -5 | tr '\n' '|')"; log "RC=$rc"; return $rc; }
INNER='flock -n /dev/shm/sldb1-tests.lock true; echo rc=$?'
log "=== Validación 4: inicio. host: $(id)"
log "lslocks antes: $(lslocks 2>/dev/null | grep sldb1 | tr -s ' ' | tr '\n' '|')"
rm -f $M
# Caso A: host sostiene
log "CMD(bg): flock -w 3600 $L bash -c 'touch held.marker; sleep 40; rm held.marker'"
flock -w 3600 $L bash -c "touch $M; sleep 40; rm -f $M" &
HP=$!
while [ ! -f $M ] && kill -0 $HP 2>/dev/null; do sleep 2; done
if [ ! -f $M ]; then wait $HP; log "holder no obtuvo el lock rc=$?"; exit 1; fi
log "host holder adquirió el lock"
run flock -n $L true   # esperado 1
run docker run --rm --user 1001:1001 -v /dev/shm:/dev/shm --entrypoint bash $IMG -c "$INNER"
run docker run --rm -e SCION_HOST_UID=1001 -e SCION_HOST_GID=1001 -v /dev/shm:/dev/shm $IMG bash -c "id; $INNER"
log "marker aún presente (dentro de los 40 s): $([ -f $M ] && echo yes || echo NO)"
wait $HP; log "holder terminó rc=$?"
# Caso B: libre
end=$((SECONDS+3600)); n=0
while [ $SECONDS -lt $end ]; do
  n=$((n+1))
  flock -n $L true; frc=$?
  if [ $frc -ne 0 ]; then log "intento $n: lock tomado por otro (host flock -n rc=$frc); espero flock -w 300"; flock -w 300 $L true; continue; fi
  log "intento $n: host flock -n rc=0 (libre)"
  run docker run --rm --user 1001:1001 -v /dev/shm:/dev/shm --entrypoint bash $IMG -c "$INNER"
  o1=$out
  run docker run --rm -e SCION_HOST_UID=1001 -e SCION_HOST_GID=1001 -v /dev/shm:/dev/shm $IMG bash -c "id; $INNER"
  o2=$out
  run docker run --rm -v /dev/shm:/dev/shm --entrypoint bash $IMG -c "id; $INNER"
  log "lslocks tras intento: $(lslocks 2>/dev/null | grep sldb1 | tr -s ' ' | tr '\n' '|')"
  if echo "$o1" | grep -q 'rc=0'; then log "Caso libre OK"; break; fi
  log "rc!=0 en caso libre; reintento"; flock -w 300 $L true
done
log "=== fin"
