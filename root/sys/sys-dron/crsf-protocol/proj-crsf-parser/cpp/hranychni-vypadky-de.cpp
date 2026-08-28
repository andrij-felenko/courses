// Додатковий запобіжник: скид парсера за тишею на лінії.
// micros() — монотонний час у мкс. Кличемо разом із crsf_parser_push.
#define CRSF_FRAME_TIMEOUT_US 1750u   // трохи більше за час 64 Б на 420k

void crsf_parser_push_timed(CrsfParser *p, uint8_t byte, uint32_t now_us) {
    static uint32_t frame_start_us = 0;
    if (p->state != ST_SYNC &&
        (uint32_t)(now_us - frame_start_us) > CRSF_FRAME_TIMEOUT_US) {
        crsf_parser_reset(p);   // задовга пауза → кинути недобраний кадр
    }
    if (p->state == ST_SYNC)
        frame_start_us = now_us;    // засікаємо початок нового кадру
    crsf_parser_push(p, byte);
}
