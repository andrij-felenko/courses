# Компіляція версії на мові C
gcc -O2 -Wall -std=c99 mptcp_client.c -o mptcp_client_c

# Компіляція версії на мові C++20
g++ -O2 -Wall -std=c++20 mptcp_client.cpp -o mptcp_client_cpp

# Перевірка наявності ендпоінтів у ядрі перед запуском
ip mptcp endpoint show

# Запуск монітора подій MPTCP у сусідній термінальній сесії
ip mptcp monitor

# Запуск C++ клієнта
./mptcp_client_cpp 127.0.0.1 8080
