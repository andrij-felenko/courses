#!/bin/sh
# усе, що визначає поведінку overcommit і OOM на цій машині
sysctl vm.overcommit_memory vm.overcommit_ratio vm.overcommit_kbytes \
       vm.admin_reserve_kbytes vm.user_reserve_kbytes vm.min_free_kbytes \
       vm.panic_on_oom vm.oom_kill_allocating_task vm.oom_dump_tasks

grep -E '^(MemTotal|SwapTotal|CommitLimit|Committed_AS)' /proc/meminfo

# десятка найімовірніших жертв просто зараз
for p in /proc/[0-9]*; do
    [ -r "$p/oom_score" ] || continue
    printf '%s\t%s\t%s\n' "$(cat "$p/oom_score")" "${p#/proc/}" \
                          "$(tr -d '\0' < "$p/comm")"
done | sort -rn | head
