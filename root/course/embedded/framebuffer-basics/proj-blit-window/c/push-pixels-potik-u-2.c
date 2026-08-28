/* Запасний варіант, коли ні HW-swap, ні «дротового» буфера немає:
   переганяємо блок у тимчасовий буфер уже переверненим — одним проходом. */
static void push_pixels_swap(const uint16_t *px, size_t n)
{
    static uint16_t line[320];          // буфер на один рядок, у флеш не лізе
    while (n) {
        size_t chunk = (n < 320) ? n : 320;
        for (size_t i = 0; i < chunk; i++)
            line[i] = (uint16_t)((px[i] >> 8) | (px[i] << 8));   // swap16
        send_data((const uint8_t *)line, chunk * 2);            // блок цілком
        px += chunk;
        n  -= chunk;
    }
}
