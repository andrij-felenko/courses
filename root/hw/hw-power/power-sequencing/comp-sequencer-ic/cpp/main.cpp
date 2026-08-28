// Розпорядник сидить на шині PMBus (двопровідній, як I²C) за адресою 0x40.
#define SEQ_ADDR        0x40
#define CMD_READ_VOUT   0x8B    // стандартна команда PMBus: напруга каналу
#define CMD_STATUS_WORD 0x79    // зведений статус: є збій / який саме

// Прочитати напругу одного каналу (повертає «сире» 16-розрядне слово).
static uint16_t seq_read_vout(uint8_t channel) {
    pmbus_write_byte(SEQ_ADDR, 0x00, channel);   // PAGE: обрати канал
    return pmbus_read_word(SEQ_ADDR, CMD_READ_VOUT);
}

void seq_first_check(void) {
    uint16_t st = pmbus_read_word(SEQ_ADDR, CMD_STATUS_WORD);
    if (st == 0xFFFF) {              // шина «висить» у одиницях — чип не відповів
        log("seq: немає відповіді — перевір живлення й адресу");
        return;
    }
    for (uint8_t ch = 0; ch < 4; ch++) {
        uint16_t v = seq_read_vout(ch);
        log("seq: канал %u = %u (сире)", ch, v);   // звірити з очікуваним рівнем
    }
}
