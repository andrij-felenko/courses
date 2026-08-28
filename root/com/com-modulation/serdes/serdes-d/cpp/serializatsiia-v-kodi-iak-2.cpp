// Зібрати байт із восьми прийнятих бітів, старший прийшов першим.
uint8_t deserialize_byte(void)
{
    uint8_t data = 0;
    for (int i = 0; i < 8; i++) {
        wait_clock_edge();          // дочекатися фронту такту
        data = (data << 1) | read_line();   // зсунули ліворуч і вклали новий біт
    }
    return data;
}
