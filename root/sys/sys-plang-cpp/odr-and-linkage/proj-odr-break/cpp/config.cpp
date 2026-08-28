// config.cpp — збирається З -DWITH_TIMESTAMP
#include "packet.hpp"

Packet* make_batch(int n) {
    Packet* p = new Packet[n];
    for (int i = 0; i < n; ++i) {
        p[i].id  = i;
        p[i].len = 100 + i;
#ifdef WITH_TIMESTAMP
        p[i].ts  = 1700000000000LL + i;
#endif
    }
    return p;
}

void free_batch(Packet* p) { delete[] p; }
