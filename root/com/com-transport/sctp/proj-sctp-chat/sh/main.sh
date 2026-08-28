# 1. Завантаження модуля ядра SCTP
sudo modprobe sctp

# 2. Встановлення пакетів розробки (для Ubuntu/Debian)
sudo apt-get install -y libsctp-dev lksctp-tools

# 3. Компіляція серверної та клієнтської частини на C
gcc -O2 -Wall sctp_server.c -o sctp_server -lsctp
gcc -O2 -Wall sctp_client.c -o sctp_client -lsctp

# 4. Або компіляція на C++20
g++ -std=c++20 -O2 -Wall sctp_server.cpp -o sctp_server_cpp -lsctp
g++ -std=c++20 -O2 -Wall sctp_client.cpp -o sctp_client_cpp -lsctp
