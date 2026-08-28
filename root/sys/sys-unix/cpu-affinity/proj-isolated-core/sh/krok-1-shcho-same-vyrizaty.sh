# загальна картина: логічне ядро → фізичне → гніздо → вузол пам'яті
lscpu -e=CPU,CORE,SOCKET,NODE,ONLINE

# сусідня нитка конкретного логічного ядра
cat /sys/devices/system/cpu/cpu6/topology/thread_siblings_list
6,38

# до якого вузла пам'яті це ядро належить
ls -d /sys/devices/system/cpu/cpu6/node*
/sys/devices/system/cpu/cpu6/node0
