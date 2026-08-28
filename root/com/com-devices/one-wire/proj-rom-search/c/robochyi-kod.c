uint8_t ROM_NO[8];                 /* адреса, що будується цим проходом      */
static int  LastDiscrepancy;       /* найглибша неопрацьована розвилка (1..64)*/
static int  LastFamilyDiscrepancy; /* те саме в межах першого байта (родини)  */
static bool LastDeviceFlag;        /* останній пристрій уже знайдено          */
static uint8_t crc8;               /* накопичувальний залишок CRC             */

/* Команда пошуку: 0xF0 — усі пристрої; 0xEC — лише зі зведеною тривогою */
uint8_t OWSearchCommand = 0xF0;

/* CRC-8/Dallas, поліном X⁸+X⁵+X⁴+1 (віддзеркалений — 0x8C), накопичувальний */
static uint8_t docrc8(uint8_t value)
{
    crc8 ^= value;
    for (int i = 0; i < 8; i++)
        crc8 = (crc8 & 1) ? (crc8 >> 1) ^ 0x8C : (crc8 >> 1);
    return crc8;
}
