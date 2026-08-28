/* Груба, але надійна ознака: якщо перші чотири байти прочитати
   як довжину, вона має привести рівно до наступного заголовка NAL. */
static int looks_length_prefixed(const uint8_t *b, long n)
{
    if (n < 5) return 0;
    if (b[0] == 0 && b[1] == 0 && (b[2] == 1 || (b[2] == 0 && b[3] == 1))) return 0;

    uint32_t len = ((uint32_t)b[0] << 24) | ((uint32_t)b[1] << 16) |
                   ((uint32_t)b[2] <<  8) |  (uint32_t)b[3];
    long next = 4 + (long)len;
    if (len == 0 || next >= n) return 0;
    return (b[next] & 0x80) == 0 && (b[next] & 0x1Fu) != 0;
}
