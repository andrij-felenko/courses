# Перевірка куди вказують дескриптори в інтерактивному терміналі
ls -l /proc/self/fd/
# lrwx------ 0 user group -> /dev/pts/1
# lrwx------ 1 user group -> /dev/pts/1
# lrwx------ 2 user group -> /dev/pts/1

# Перевірка дескрипторів при перенаправленні stdout у файл
ls -l /proc/self/fd/ > fds.txt && cat fds.txt
# lrwx------ 0 user group -> /dev/pts/1
# l-wx------ 1 user group -> /home/user/fds.txt
# lrwx------ 2 user group -> /dev/pts/1

# Перевірка дескрипторів всередині конвеєра
ls -l /proc/self/fd/ | cat
# lrwx------ 0 user group -> pipe:[482910]
# l-wx------ 1 user group -> /dev/pts/1
# lrwx------ 2 user group -> /dev/pts/1
