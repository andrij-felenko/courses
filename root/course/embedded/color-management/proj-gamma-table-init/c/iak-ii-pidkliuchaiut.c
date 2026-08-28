/* lcd_cmd(cmd, data, len): шле байт-команду (DC=0), потім len байтів
   параметрів (DC=1) — той самий помічник, що й для решти ініту.    */

/* (опційно) вибір базової кривої / увімкнення правленої гами.
   Значення 0x01 = крива «G2.2» — типовий старт.                    */
static const uint8_t gamma_set[] = { 0x01 };
lcd_cmd(0x26, gamma_set, 1);                 /* Gamma Set            */

/* Позитивна гама — 15 зломів (значення з даташита ПАНЕЛІ, не з неба) */
static const uint8_t gmctrp1[] = {
    0x0F, 0x31, 0x2B, 0x0C, 0x0E, 0x08, 0x4E, 0xF1,
    0x37, 0x07, 0x10, 0x03, 0x0E, 0x09, 0x00
};
lcd_cmd(0xE0, gmctrp1, sizeof(gmctrp1));     /* Positive Gamma       */

/* Негативна гама — дзеркальний, але ОКРЕМИЙ набір (проти мерехтіння) */
static const uint8_t gmctrn1[] = {
    0x00, 0x0E, 0x14, 0x03, 0x11, 0x07, 0x31, 0xC1,
    0x48, 0x08, 0x0F, 0x0C, 0x31, 0x36, 0x0F
};
lcd_cmd(0xE1, gmctrn1, sizeof(gmctrn1));     /* Negative Gamma       */
