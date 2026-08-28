#!/bin/sh
# watch-state.sh <pid> [період_мс] — смуга станів одного процесу.
pid=$1
per=${2:-50}
[ -r "/proc/$pid/stat" ] || { echo "немає процесу $pid" >&2; exit 1; }

start=$(date +%s.%N)
nap=$(awk -v p="$per" 'BEGIN{ print p/1000 }')
prev='' band='' held=0 cont=0

elapsed() { awk -v a="$(date +%s.%N)" -v b="$start" 'BEGIN{ printf "%7.3f", a-b }'; }

while [ -r "/proc/$pid/stat" ]; do
    line=$(cat "/proc/$pid/stat" 2>/dev/null) || break
    [ -n "$line" ] || break
    st=${line##*") "}          # ім'я програми може містити ')' — ріжемо по останній
    st=${st%% *}
    band="$band$st"

    if [ "$st" != "$prev" ]; then
        wch=$(cat "/proc/$pid/wchan" 2>/dev/null || echo '?')
        printf '%s  %s   wchan=%s\n' "$(elapsed)" "$st" "$wch"
        prev=$st; held=0
    fi

    held=$((held + 1))
    if [ "$st" = T ] && [ "$cont" -eq 0 ] && [ "$held" -gt $((2000 / per)) ]; then
        kill -CONT "$pid"; cont=1
        printf '%s  →   надіслано SIGCONT\n' "$(elapsed)"
    fi

    sleep "$nap"
done

printf '\nсмуга: %s\n' "$band"
