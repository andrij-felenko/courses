# VSZ і RSS у KiB, без запуску ps
awk '/^VmSize:/ {vsz=$2} /^VmRSS:/ {rss=$2} END {print vsz, rss}' /proc/$$/status

# PSS у KiB
awk '/^Pss:/ {print $2}' /proc/$$/smaps_rollup

# USS: те, що звільниться негайно після смерті процесу
awk '/^Private_(Clean|Dirty):/ {s+=$2} END {print s}' /proc/$$/smaps_rollup

# реальна потреба в пам'яті: заселене плюс витіснене
awk '/^VmRSS:/ {r=$2} /^VmSwap:/ {s=$2} END {print r+s}' /proc/$$/status

# найдорожчі ділянки за PSS, з іменами
awk '/^[0-9a-f]+-/ {name = (NF >= 6) ? $6 : "[анонімне]"}
     /^Pss:/       {p[name] += $2}
     END           {for (n in p) print p[n], n}' /proc/$$/smaps | sort -rn | head
