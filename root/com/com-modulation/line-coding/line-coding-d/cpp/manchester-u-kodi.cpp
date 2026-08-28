// Викласти один біт даних як дві половинки манчестерського символу.
// set_line(level) кладе рівень; half_tick() витримує півтакту.
// Конвенція IEEE 802.3: 1 → низько-високо, 0 → високо-низько.
void manchester_send_bit(uint8_t bit)
{
    if (bit) {                 // одиниця: перехід угору посеред біта
        set_line(0); half_tick();
        set_line(1); half_tick();
    } else {                   // нуль: перехід униз посеред біта
        set_line(1); half_tick();
        set_line(0); half_tick();
    }
}
