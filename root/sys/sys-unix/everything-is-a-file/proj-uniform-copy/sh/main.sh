cc -O2 -Wall -Wextra -o copyfd copyfd.c

# 1. звичайний файл
./copyfd /etc/services out.txt && cmp /etc/services out.txt && echo збіглося

# 2. канал: писар працює просто зараз і віддає порціями
dmesg | ./copyfd - kernel.log

# 3. термінал: читає, доки не натиснути Ctrl-D
./copyfd /dev/tty typed.txt

# 4. TCP-сокет: socat приймає з'єднання й віддає його нам у дескриптори 0 і 1
socat TCP-LISTEN:9000,reuseaddr 'EXEC:./copyfd - from-net.txt,nofork'
#    в іншому вікні:
printf 'привіт із дроту\n' | socat - TCP:localhost:9000
