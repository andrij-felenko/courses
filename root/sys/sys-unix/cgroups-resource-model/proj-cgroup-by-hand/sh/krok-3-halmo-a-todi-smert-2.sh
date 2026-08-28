echo max > "$CG/lab/memory.high"     # знімаємо гальмо, лишаємо саму стелю
echo 64M > "$CG/lab/memory.max"
echo 0   > "$CG/lab/memory.swap.max" # інакше група тихо піде у своп
echo 1   > "$CG/lab/memory.oom.group"

( echo $BASHPID > "$CG/lab/cgroup.procs"; exec ./hog )
echo "код виходу: $?"
# 8 МіБ
# …
# 56 МіБ
# код виходу: 137
