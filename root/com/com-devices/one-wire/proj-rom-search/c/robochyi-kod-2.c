bool OWSearch(void)
{
    int id_bit_number   = 1;       /* 1..64 — котрий біт адреси зараз          */
    int last_zero       = 0;       /* де цього проходу обрали 0 на розвилці    */
    int rom_byte_number = 0;
    uint8_t rom_byte_mask = 1;
    bool search_result  = false;
    crc8 = 0;

    if (!LastDeviceFlag) {
        if (!OWReset()) {                     /* немає присутності — шина порожня */
            LastDiscrepancy = 0;
            LastDeviceFlag = false;
            LastFamilyDiscrepancy = 0;
            return false;
        }
        OWWriteByte(OWSearchCommand);         /* 0xF0 (або 0xEC для тривоги) */

        do {
            uint8_t id_bit     = OWReadBit(); /* прямий біт   */
            uint8_t cmp_id_bit = OWReadBit(); /* інверсний біт */

            if (id_bit && cmp_id_bit)         /* (1,1) — ніхто не відповів */
                break;                         /* прохід зіпсовано, вийти   */

            uint8_t search_direction;
            if (id_bit != cmp_id_bit) {
                /* (0,1) або (1,0) — усі згодні: гілку задає сам біт */
                search_direction = id_bit;
            } else {
                /* (0,0) — розвилка: є і 0, і 1, обираємо напрям */
                if (id_bit_number < LastDiscrepancy)
                    /* мілкіше за закладку — повторюємо торішній вибір */
                    search_direction = (ROM_NO[rom_byte_number] & rom_byte_mask) ? 1 : 0;
                else
                    /* на самій закладці — тепер 1; глибше за неї — 0 */
                    search_direction = (id_bit_number == LastDiscrepancy) ? 1 : 0;

                if (search_direction == 0) {
                    last_zero = id_bit_number;         /* тут лишилась гілка 1 на потім */
                    if (last_zero < 9)
                        LastFamilyDiscrepancy = last_zero;
                }
            }

            /* записати обраний біт у ROM_NO ... */
            if (search_direction)
                ROM_NO[rom_byte_number] |=  rom_byte_mask;
            else
                ROM_NO[rom_byte_number] &= ~rom_byte_mask;

            /* ... і оголосити його шині: невідповідні ведені замовкають */
            OWWriteBit(search_direction);

            id_bit_number++;
            rom_byte_mask <<= 1;
            if (rom_byte_mask == 0) {                  /* байт зібрано цілком */
                docrc8(ROM_NO[rom_byte_number]);       /* накопичити CRC     */
                rom_byte_number++;
                rom_byte_mask = 1;
            }
        } while (rom_byte_number < 8);                 /* усі 64 біти */

        /* успіх лише якщо пройшли всі 64 біти і CRC зійшовся (залишок 0) */
        if (id_bit_number >= 65 && crc8 == 0) {
            LastDiscrepancy = last_zero;
            if (LastDiscrepancy == 0)
                LastDeviceFlag = true;                 /* глибших розвилок нема — останній */
            search_result = true;
        }
    }

    if (!search_result || ROM_NO[0] == 0) {            /* нічого не знайшли — скинути стан */
        LastDiscrepancy = 0;
        LastDeviceFlag = false;
        LastFamilyDiscrepancy = 0;
        search_result = false;
    }
    return search_result;
}
