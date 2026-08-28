#!/bin/sh
echo "── розміри, які вміє машина ──"
ls -1 /sys/kernel/mm/hugepages/

echo "── пул ──"
grep -E 'HugePages_|Hugepagesize|^Hugetlb' /proc/meminfo

echo "── THP: вимикачі ──"
for f in enabled defrag shrink_underused hpage_pmd_size; do
        printf '%-18s %s\n' "$f" "$(cat /sys/kernel/mm/transparent_hugepage/$f)"
done

echo "── THP: скільки вже лежить під великими сторінками ──"
grep -E 'AnonHugePages|ShmemHugePages|FileHugePages|ShmemPmdMapped' /proc/meminfo

echo "── чи вдаються спроби ──"
grep -E '^(thp_fault_alloc|thp_fault_fallback|thp_collapse_alloc|compact_stall) ' /proc/vmstat

echo "── що дісталося процесові $1 ──"
awk '/^[0-9a-f]+-/ { rng=$0 }
     /^AnonHugePages:/ && $2 > 0 { print rng; print "  " $0 }' "/proc/$1/smaps"
