#include <cstddef>
#include <iostream>

struct PacketHeader {
    char flag;       // 1 байт
    int id;          // 4 байти
    double weight;   // 8 байтів
};

static_assert(alignof(char) == 1);
static_assert(alignof(int) == 4);
static_assert(alignof(double) == 8);
static_assert(alignof(PacketHeader) == 8); // визначається найбільшим членом
