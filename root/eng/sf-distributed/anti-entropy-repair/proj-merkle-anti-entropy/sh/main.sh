# Збільшення розміру буферів прийому та відправки мережевого стека для високих швидкостей потокової передачі
sysctl -w net.core.rmem_max=16777216
sysctl -w net.core.wmem_max=16777216
sysctl -w net.ipv4.tcp_rmem="4096 87380 16777216"
sysctl -w net.ipv4.tcp_wmem="4096 65536 16777216"

# Оптимізація поведінки фонового скидання брудних сторінок пам'яті на диск
sysctl -w vm.dirty_background_ratio=5
sysctl -w vm.dirty_ratio=10

# Вимкнення агресивного swap-механізму для захисту процесів бази даних від затримок
sysctl -w vm.swappiness=1
