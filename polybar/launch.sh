#!/bin/sh
# Uma barra por monitor conectado; no modo foco (focus), só a contagem regressiva.
# flock: theme, focus e o i3 podem chamar isto ao mesmo tempo, e duas chamadas juntas dobravam as barras.
exec 9>"${XDG_RUNTIME_DIR:-/tmp}/polybar-launch.lock"
flock 9
bar=main
[ -f "${XDG_CACHE_HOME:-$HOME/.cache}/focus" ] && bar=focus
# às vezes a polybar não sai com SIGTERM (fica presa durante um reload do i3): espera 3 s e mata de vez
pkill -x polybar
i=0
while pgrep -x polybar >/dev/null && [ $i -lt 30 ]; do sleep 0.1; i=$((i + 1)); done
pkill -9 -x polybar
for m in $(polybar --list-monitors | cut -d: -f1); do
  MONITOR=$m setsid -f polybar --reload "$bar" >/dev/null 2>&1 9>&-
done
sleep 0.5
