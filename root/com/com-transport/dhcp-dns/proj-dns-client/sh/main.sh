# Компіляція версії на C
gcc -O2 -Wall -Wextra -pedantic proj-dns-client.c -o dns_client_c

# Компіляція версії на C++ (стандарт C++20)
g++ -O2 -Wall -Wextra -std=c++20 proj-dns-client.cpp -o dns_client_cpp

# Тестування резолвінгу через публічний сервер Cloudflare (1.1.1.1)
./dns_client_cpp example.com 1.1.1.1

# Тестування резолвінгу через публічний сервер Google (8.8.8.8)
./dns_client_c wikipedia.org 8.8.8.8
