struct Sub { uint32_t z, x, y; int px, py, side; };

// Предок на k рівнів вище і підквадрат у ньому, що відповідає тайлові (z,x,y)
static Sub ancestor(uint32_t z, uint32_t x, uint32_t y, uint32_t k)
{
    uint32_t side = 256u >> k;        // сторона підквадрата в пікселях предка
    uint32_t mask = (1u << k) - 1;    // молодші k бітів = положення всередині предка
    return Sub{ z - k, x >> k, y >> k,
                (int)((x & mask) * side), (int)((y & mask) * side), (int)side };
}
