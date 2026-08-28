$ sudo dmesg -t | awk '
     /^entering initcall level:/ { lvl = $4
         if (!(lvl in total)) { order[++k] = lvl; total[lvl] = 0 }
         next }
     $1 == "initcall" && $NF == "usecs" { n[lvl]++; total[lvl] += $(NF-1) }
     END { for (i = 1; i <= k; i++) { l = order[i]
             printf "%-9s %4d викликів %9.1f мс\n", l, n[l], total[l] / 1000 } }'
early        14 викликів       3.1 мс
core         96 викликів      41.7 мс
...
device      612 викликів    1284.9 мс
late         88 викликів     102.4 мс
