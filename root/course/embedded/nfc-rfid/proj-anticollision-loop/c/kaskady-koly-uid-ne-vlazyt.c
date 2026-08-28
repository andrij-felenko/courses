// Прочитати ПОВНИЙ UID однієї картки (обійшовши всі каскади) і вибрати її.
// uid_out — до 10 байтів; повертає довжину UID (4/7/10) або 0 при помилці.
// sak_final — SAK останнього каскаду (тип картки).
static uint8_t picc_select_full(uint8_t uid_out[10], uint8_t *sak_final)
{
    const uint8_t sels[3] = { SEL_CL1, SEL_CL2, SEL_CL3 };
    uint8_t uid_len = 0;

    for (uint8_t cl = 0; cl < 3; cl++) {
        uint8_t block[4], sak;
        pcd_status_t s = select_level(sels[cl], block, &sak);
        if (s != PCD_OK)
            return 0;                        // збій десь у дереві

        if (block[0] == CMD_CT && (sak & 0x04)) {
            // Cascade Tag присутній → байти 1..3 блоку реальні, каскад триває.
            memcpy(&uid_out[uid_len], &block[1], 3);
            uid_len += 3;
        } else {
            // Останній каскад → усі 4 байти блоку — частина UID.
            memcpy(&uid_out[uid_len], block, 4);
            uid_len += 4;
            *sak_final = sak;
            return uid_len;                  // 4, 7 або 10
        }
    }
    return 0;                                // теоретично недосяжно
}
