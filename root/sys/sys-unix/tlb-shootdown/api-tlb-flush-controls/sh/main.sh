cd /sys/kernel/tracing            # на старих системах /sys/kernel/debug/tracing

# 1. Увімкнути точку й подивитися потік
echo 1 > events/tlb/tlb_flush/enable
cat trace_pipe
#  munmap-4821  [017] .... 91231.442: tlb_flush: pages:33 reason:remote IPI send (4)
#  <idle>-0     [042] d.h. 91231.442: tlb_flush: pages:33 reason:remote shootdown (1)

# 2. Лише розсилання (обидва боки), решту відсіяти
echo 'reason == 1 || reason == 4' > events/tlb/tlb_flush/filter

# 3. Гістограма розмірів діапазону — ось звідки видно, чи впирається він у стелю
echo 'hist:key=pages.log2:val=hitcount' > events/tlb/tlb_flush/trigger
cat events/tlb/tlb_flush/hist

# 4. Прибрати за собою
echo 0 > events/tlb/tlb_flush/enable
echo '!hist:key=pages.log2' > events/tlb/tlb_flush/trigger
echo 0 > events/tlb/tlb_flush/filter
