irqsnap() {                       # $1 — номер логічного ядра
  awk -v c="$1" '
    NR == 1 { n = NF; for (i = 1; i <= NF; i++) if ($i == ("CPU" c)) col = i + 1; next }
    col && NF > n { print $1, $col }
  ' /proc/interrupts
}

irqsnap 6 > /tmp/irq.a; sleep 10; irqsnap 6 > /tmp/irq.b
awk 'NR == FNR { a[$1] = $2; next } $2 > a[$1] { printf "%-8s +%d\n", $1, $2 - a[$1] }' \
    /tmp/irq.a /tmp/irq.b
