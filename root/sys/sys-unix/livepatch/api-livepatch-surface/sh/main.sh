# які латки стоять і в якому вони стані
for p in /sys/kernel/livepatch/*/; do
        printf '%s enabled=%s transition=%s\n' \
                "$(basename "$p")" "$(cat "$p/enabled")" "$(cat "$p/transition")"
done

# що саме залатано у верхній латці
find /sys/kernel/livepatch/<латка> -mindepth 2 -maxdepth 2 -type d

# хто ще не перемкнувся, з іменами
for f in $(grep -l '^0$' /proc/[0-9]*/patch_state); do
        pid=${f%/patch_state}; printf '%s %s\n' "${pid#/proc/}" "$(cat "$pid/comm")"
done
