echo 1 | sudo tee /sys/kernel/mm/ksm/run

# рушило чи ні: full_scans мусить рости, pages_sharing — теж
grep -H '' /sys/kernel/mm/ksm/{run,full_scans,pages_shared,pages_sharing,general_profit}

# що дісталося саме нашому процесу
cat /proc/$PID/ksm_stat

# і чи справді ядро взяло ділянку — позначка mg
grep -A24 "^$(printf %x $ADDR)" /proc/$PID/smaps | grep -E '^(KSM|VmFlags):'
