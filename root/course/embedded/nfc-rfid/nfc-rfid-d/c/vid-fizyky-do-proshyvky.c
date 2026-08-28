#include <stdint.h>
#include <stdbool.h>

// Команда PN532: InListPassiveTarget — знайти пасивну ціль 106 кбіт/с Type A.
// PN532 сам робить ВСЮ фізику: поле, живлення картки, антиколізію, SELECT.
#define PN532_CMD_INLISTPASSIVE  0x4A
#define PN532_MIFARE_ISO14443A   0x00

// Надіслати кадр команди PN532 і забрати відповідь (SPI-обгортки нижче опущено).
bool pn532_send_command(const uint8_t *cmd, uint8_t clen,
                        uint8_t *resp, uint8_t *rlen);

// Прочитати UID першої картки в полі. Повертає довжину UID (4/7/10) або 0.
uint8_t nfc_read_uid(uint8_t *uid_out)
{
    // Аргументи: [команда][макс. цілей = 1][тип = Type A 106k]
    uint8_t cmd[3] = { PN532_CMD_INLISTPASSIVE, 0x01, PN532_MIFARE_ISO14443A };
    uint8_t resp[32];
    uint8_t rlen = sizeof(resp);

    if (!pn532_send_command(cmd, sizeof(cmd), resp, &rlen))
        return 0;                    // немає відповіді від контролера

    // Формат відповіді InListPassiveTarget:
    //   resp[0] = кількість знайдених цілей (0, якщо картки немає)
    //   resp[1] = номер цілі (Tg)
    //   resp[2..3] = SENS_RES (ATQA), resp[4] = SEL_RES (SAK)
    //   resp[5] = довжина UID
    //   resp[6..] = сам UID
    if (rlen < 6 || resp[0] == 0)
        return 0;                    // у полі немає картки

    uint8_t uid_len = resp[5];
    if (uid_len == 0 || uid_len > 10 || (uint8_t)(6 + uid_len) > rlen)
        return 0;                    // захист від побитого кадру

    for (uint8_t i = 0; i < uid_len; i++)
        uid_out[i] = resp[6 + i];

    return uid_len;                  // 4, 7 або 10 — залежно від типу картки
}
