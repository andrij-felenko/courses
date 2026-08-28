# у якій функції ядра задача викликала schedule()
ps -eo pid,stat,wchan:32,comm | grep ' D'
cat /proc/2431/wchan

# повний стек ядра застряглої задачі — видно і макрос очікування, і драйвер під ним
sudo cat /proc/2431/stack

# хто кого будить: події планувальника в реальному часі
sudo perf record -e sched:sched_wakeup -e sched:sched_switch -a -- sleep 5
sudo perf script | head -40
