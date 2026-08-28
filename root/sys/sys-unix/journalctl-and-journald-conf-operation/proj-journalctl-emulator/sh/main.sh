# Компіляція версії на C за допомогою GCC
gcc -O2 -Wall -Wextra journal_reader.c -lsystemd -o journal_reader

# Компіляція версії на C++ (потрібен компілятор із підтримкою стандарту C++20/C++23)
g++ -std=c++23 -O2 -Wall -Wextra journal_reader.cpp -lsystemd -o journal_reader_cpp

# Запуск перевірки логів системного сервісу SSH
./journal_reader sshd.service

# Запуск перевірки логів сервісу управління мережею
./journal_reader_cpp NetworkManager.service
