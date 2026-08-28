// packet.hpp
#pragma once
#include <cstddef>

struct Packet {
    int id;
    int len;
#ifdef WITH_TIMESTAMP
    long long ts;                 // ← поле є лише в частині збірки
#endif
    static std::size_t stride() { return sizeof(Packet); }   // inline
};

Packet* make_batch(int n);        // визначено в config.cpp
void    free_batch(Packet* p);
