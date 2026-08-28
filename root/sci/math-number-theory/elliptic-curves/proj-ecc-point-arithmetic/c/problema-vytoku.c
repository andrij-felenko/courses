void cswap(uint64_t bit, Point* P, Point* Q) {
    uint64_t mask = -bit; // 0x0000... якщо bit=0, 0xFFFF... якщо bit=1
    uint64_t delta_x = mask & (P->x ^ Q->x);
    P->x ^= delta_x;
    Q->x ^= delta_x;
    
    uint64_t delta_y = mask & (P->y ^ Q->y);
    P->y ^= delta_y;
    Q->y ^= delta_y;
}
