# 1. Інсталяція необхідних системних бібліотек розробки OpenSSL
sudo apt-get install build-essential libssl-dev

# 2. Збірка варіанту C++20
g++ -std=c++20 tpm2_log_parser.cpp -lssl -lcrypto -o tpm2_log_parser

# 3. Збірка варіанту C11
gcc -std=c11 tpm2_log_parser.c -lssl -lcrypto -o tpm2_log_parser_c

# 4. Запуск аналізу
./tpm2_log_parser

# 5. Порівняння з дійсним значенням із sysfs ядра Linux
cat /sys/class/tpm/tpm0/pcr-sha256/0
