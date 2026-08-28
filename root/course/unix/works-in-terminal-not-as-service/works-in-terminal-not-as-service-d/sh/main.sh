# Отримання PID служби
PID=$(systemctl show --property MainPID --value myapp.service)

# Перевірка реальних змінних оточення процесу
xargs -0 -L1 echo < /proc/$PID/environ

# Перевірка поточного робочого каталогу (CWD)
ls -ld /proc/$PID/cwd

# Перевірка відкритих файлових дескрипторів та точок перенаправлення
ls -l /proc/$PID/fd/

# Перевірка встановлених лімітів ресурсів
cat /proc/$PID/limits
