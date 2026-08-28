// Стани ініціалізації SD по SPI — прямо з графа.
typedef enum {
    ST_POWER,     // щойно ввімкнули: чекаємо стабілізації живлення
    ST_WARMUP,    // ≥ 74 такти при CS=1
    ST_IDLE,      // після CMD0: картка в спокої, у SPI-режимі
    ST_IFCOND,    // CMD8: звірка вольтажу й версії
    ST_POLL,      // ACMD41 у циклі, доки картка не звільниться
    ST_READY,     // CMD58 прочитано: готова, тип відомий
    ST_ERROR      // глухий кут: мовчить або таймаут
} sd_state_t;

typedef struct { sd_state_t state; int hc; int tries; } sd_fsm_t;  // hc: 1 якщо SDHC

// Один крок автомата: виконати дію поточного стану й повернути наступний стан.
// (sd_cmd — послати 6-байтову команду і дочекатися R1; визначена деінде.)
static sd_state_t sd_step(sd_fsm_t *m) {
    switch (m->state) {

    case ST_POWER:
        delay_ms(2);                 // ≥ 1 мс після появи напруги
        return ST_WARMUP;

    case ST_WARMUP:
        spi_set_clock_slow();        // 100–400 кГц на весь час ініціалізації
        CS_HIGH();
        for (int i = 0; i < 10; i++) spi_xchg(0xFF);  // ≥ 74 такти, CS високий
        return ST_IDLE;

    case ST_IDLE:
        CS_LOW();
        if (sd_cmd(0, 0, 0x94) != 0x01)   // CMD0: чекаємо рівно 0x01 (idle)
            return ST_ERROR;              // мовчить/не той стан -> глухий кут
        return ST_IFCOND;

    case ST_IFCOND:
        // CMD8: сучасна картка луною поверне 0x1AA у 4-байтовому «хвості» R7.
        // «Недозволена» (біт 0x04) означає стару картку — теж прямуємо в POLL.
        sd_cmd(8, 0x000001AA, 0x86);
        for (int i = 0; i < 4; i++) spi_xchg(0xFF);   // забрати хвіст R7
        m->tries = 0;
        return ST_POLL;

    case ST_POLL:
        sd_cmd(55, 0, 0xFF);                          // CMD55: далі прикладна
        if (sd_cmd(41, 0x40000000, 0xFF) == 0x00)     // ACMD41, HCS=1
            return ST_READY;                          // 0x00 -> картка готова
        if (++m->tries > 1000)                        // таймаут циклу опитування
            return ST_ERROR;
        return ST_POLL;                               // ще busy -> самопетля

    case ST_READY: {
        uint8_t ocr[4];
        sd_cmd(58, 0, 0xFF);                          // CMD58: читаємо OCR
        for (int i = 0; i < 4; i++) ocr[i] = spi_xchg(0xFF);
        m->hc = (ocr[0] & 0x40) ? 1 : 0;              // біт CCS -> SDHC?
        CS_HIGH();
        spi_set_clock_fast();                         // готово -> повна частота
        return ST_READY;
    }

    default:                                          // ST_ERROR
        CS_HIGH();
        return ST_ERROR;
    }
}

// Прокрутити автомат до READY або ERROR. Повертає 0, якщо картка готова.
int sd_init_fsm(sd_fsm_t *m) {
    m->state = ST_POWER; m->hc = 0; m->tries = 0;
    while (m->state != ST_READY && m->state != ST_ERROR)
        m->state = sd_step(m);
    // ще один крок у READY зчитує OCR і піднімає частоту
    if (m->state == ST_READY) { sd_step(m); return 0; }
    return -1;                                         // ST_ERROR
}
