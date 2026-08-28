# Збірка прикладу C:
gcc -O2 -Wall -Wextra miniplex.c -lutil -o miniplex

# Або збірка прикладу C++:
g++ -std=c++23 -O2 -Wall -Wextra miniplex.cpp -lutil -o miniplex_cpp

# Запуск фонового сервера:
./miniplex --server &

# Підключення клієнта:
./miniplex --client
