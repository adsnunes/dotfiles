#!/bin/sh
# Uma barra por monitor conectado; no modo foco (focus), só a contagem regressiva.
# flock: theme, focus e o i3 podem chamar isto ao mesmo tempo, e duas chamadas juntas dobravam as barras.
exec 9>"${XDG_RUNTIME_DIR:-/tmp}/polybar-launch.lock"
flock 9
bar=main
[ -f "${XDG_CACHE_HOME:-$HOME/.cache}/focus" ] && bar=focus
pkill -x polybar
while pgrep -x polybar >/dev/null; do sleep 0.1; done
for m in $(polybar --list-monitors | cut -d: -f1); do
  MONITOR=$m setsid -f polybar --reload "$bar" >/dev/null 2>&1 9>&-
done
sleep 0.5
