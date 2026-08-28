// render.cpp — збирається БЕЗ прапорця
#include "packet.hpp"
#include <cstdio>

int main() {
    std::printf("render: sizeof=%zu stride()=%zu\n",
                sizeof(Packet), Packet::stride());

    Packet* p = make_batch(4);
    for (int i = 0; i < 4; ++i)
        std::printf("  [%d] id=%d len=%d\n", i, p[i].id, p[i].len);
    free_batch(p);
}
