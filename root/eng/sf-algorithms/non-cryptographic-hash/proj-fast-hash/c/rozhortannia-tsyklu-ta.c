/* Обробка блоків по 32 байти у C */
for (size_t i = 0; i < nblocks_by_32; i++) {
    uint64_t k1 = load64(data + i * 32 + 0);
    uint64_t k2 = load64(data + i * 32 + 8);
    uint64_t k3 = load64(data + i * 32 + 16);
    uint64_t k4 = load64(data + i * 32 + 24);

    h1 = mix_step(h1, k1);
    h2 = mix_step(h2, k2);
    h3 = mix_step(h3, k3);
    h4 = mix_step(h4, k4);
}
uint64_t h = h1 ^ h2 ^ h3 ^ h4;
