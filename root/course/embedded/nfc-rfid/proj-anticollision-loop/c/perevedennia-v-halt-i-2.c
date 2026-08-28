// Перебрати ВСІ картки в полі, викликаючи on_card() для кожної.
// max_cards — запобіжник від нескінченного циклу. Повертає кількість знайдених.
uint8_t nfc_enumerate_field(void (*on_card)(const uint8_t *uid, uint8_t len, uint8_t sak),
                            uint8_t max_cards)
{
    uint8_t atqa[2];
    uint8_t found = 0;

    pcd_field_on();

    while (found < max_cards) {
        // REQA (не WUPA!): будимо лише ще не приспаних. Уже оброблені мовчать.
        if (!picc_request(CMD_REQA, atqa))
            break;                            // у полі не лишилося активних карток

        uint8_t uid[10], sak, len;
        len = picc_select_full(uid, &sak);
        if (len == 0) {
            // Збій вибору (картку прибрали посеред дерева, завада тощо).
            // Повторимо цикл: наступний REQA перечитає, що лишилося.
            continue;
        }

        on_card(uid, len, sak);               // віддали картку застосунку
        found++;

        picc_halt();                          // прибрали її з гри → наступний REQA візьме іншу
    }

    return found;
}
