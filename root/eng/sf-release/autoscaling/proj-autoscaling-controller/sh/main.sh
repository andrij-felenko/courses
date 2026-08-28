# Перевірка обмежень процесора для контейнера
$ cat /sys/fs/cgroup/system.slice/docker-xyz.scope/cpu.max
200000 100000    # Дозволено 200 000 мкс (2 vCPU) на кожні 100 000 мкс квоти

# Отримання реального використання та тротлінгу (cgroups v2)
$ cat /sys/fs/cgroup/system.slice/docker-xyz.scope/cpu.stat
usage_usec 4819203912      # Сумарний час виконання в мікросекундах
user_usec 3912840192
system_usec 906363720
nr_periods 48201           # Кількість минулих квантів часу
nr_throttled 3412          # Скільки разів процес було насильно призупинено (throttling)
throttled_usec 89124012    # Сумарний час затримки через вичерпання ліміту CPU
