// Прошивка (фрагмент, що нас цікавить)
typedef struct { uint32_t valid; uint32_t rate; } state_t;
state_t g_state;            // у RAM (DRAM)

void flash_handler_a(void); // код у Flash
void flash_handler_b(void); // код у Flash

void ram_buffer_fill(uint8_t *p, size_t n) {  // гарячий цикл
    for (size_t i = 0; i < n; i++) p[i] = 0;  // тут хочемо спинятись
}
