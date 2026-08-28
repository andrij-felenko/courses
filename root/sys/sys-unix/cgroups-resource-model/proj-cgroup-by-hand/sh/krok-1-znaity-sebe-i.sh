echo $$ > "$CG/leaf/cgroup.procs"          # процес може перевести сам себе
echo "+cpu +memory" > "$CG/cgroup.subtree_control"

ls "$CG/lab" | grep -E '^(cpu|memory)\.' | head -6
# cpu.max
# cpu.stat
# cpu.weight
# memory.current
# memory.events
# memory.high
