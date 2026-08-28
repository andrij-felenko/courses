// 2D кодування (x: 32 біти, y: 32 біти -> z: 64 біти)
uint64_t morton_encode2d(uint32_t x, uint32_t y);

// 2D декодування (z: 64 біти -> x: 32 біти, y: 32 біти)
void morton_decode2d(uint64_t z, uint32_t *out_x, uint32_t *out_y);

// 3D кодування (x: 21 біт, y: 21 біт, z: 21 біт -> key: 64 біти)
uint64_t morton_encode3d(uint32_t x, uint32_t y, uint32_t z);

// 3D декодування
void morton_decode3d(uint64_t key, uint32_t *out_x, uint32_t *out_y, uint32_t *out_z);
