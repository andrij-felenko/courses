// Згенеровано з .rbf/.bin: сирий бітстрім як масив байтів.
extern const uint8_t fpga_bitstream[];
extern const size_t  fpga_bitstream_len;

static size_t s_pos = 0;   // поточне зміщення читання

static size_t bitstream_read(uint8_t *buf, size_t len)
{
    size_t left = fpga_bitstream_len - s_pos;
    if (left == 0) return 0;                 // дійшли до кінця
    size_t take = (left < len) ? left : len;
    for (size_t i = 0; i < take; ++i)
        buf[i] = fpga_bitstream[s_pos + i];
    s_pos += take;
    return take;
}
