# 1. Компіляція версії на мові C
gcc -Wall -Wextra -O2 -std=c11 proj_dispatcher.c -o proj_dispatcher_c

# 2. Компіляція версії на мові C++ (потрібен стандарт C++23)
g++ -Wall -Wextra -O2 -std=c++23 proj_dispatcher.cpp -o proj_dispatcher_cpp

# 3. Запуск та перевірка виводу
./proj_dispatcher_c
# Очікуваний вивід:
# [Сервер] Клієнт верифікований ядром: PID=12345, UID=1000, GID=1000
# [Сервер] Канал даних та сигналізацію успішно делеговано клієнту.
# [Клієнт] Отримано сигнал готовності (лічильник: 1).
# [Клієнт] Зміст буфера: "Еталонне повідомлення високої чіткості від майстра..."

# 4. Трасування передачі дескрипторів через strace
strace -f -e trace=socketpair,sendmsg,recvmsg,memfd_create,eventfd2 ./proj_dispatcher_c
# У лозі strace чітко видно виклик sendmsg із повідомленням SCM_RIGHTS та появу нових дескрипторів
