echo max > "$CG/lab/cpu.max"      # стеля процесора більше не потрібна
echo 64M > "$CG/lab/memory.high"

# гігабайт у кеш сторінок — руками самої групи
( echo $BASHPID > "$CG/lab/cgroup.procs"
  exec dd if=/dev/zero of="$HOME/big" bs=1M count=1024 status=none )

cat "$CG/lab/memory.current"                 # 67 076 096  — тримається біля позначки
grep -E '^(high|max|oom)' "$CG/lab/memory.events"
# high 12043
# max 0
# oom 0
