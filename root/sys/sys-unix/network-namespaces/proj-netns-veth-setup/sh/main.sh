# Компіляція прикладу мовою C
gcc -O2 -Wall -Wextra demo_netns.c -o demo_netns_c

# Компіляція прикладу мовою C++20
g++ -O2 -std=c++20 -Wall -Wextra demo_netns.cpp -o demo_netns_cpp

# Запуск із правами root (необхідно для створення просторів)
sudo ./demo_netns_c
sudo ./demo_netns_cpp

# Інспекція результату у системі
ip netns list
ip netns exec demo_c_ns ip a
