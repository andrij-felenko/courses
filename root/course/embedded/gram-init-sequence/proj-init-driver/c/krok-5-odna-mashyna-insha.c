// Аргументи ILI9341 — свої масиви у флеші.
static const uint8_t ILI_PWCTRL1[] = { 0x23 };               // керування живленням 1
static const uint8_t ILI_PWCTRL2[] = { 0x10 };               // керування живленням 2
static const uint8_t ILI_VMCTRL1[] = { 0x3E, 0x28 };         // VCOM 1 (два байти!)
static const uint8_t ILI_COLMOD[]  = { 0x55 };               // RGB565, як і в ST7789
static const uint8_t ILI_MADCTL[]  = { 0x48 };               // інша орієнтація + BGR

// Таблиця для ILI9341 — той самий формат, інші байти.
static const init_cmd_t ili9341_table[] = {
    { 0x01, 0, NULL,        150 },   // SWRESET
    { 0x11, 0, NULL,        120 },   // SLPOUT — та сама важлива пауза
    { 0xC0, 1, ILI_PWCTRL1,   0 },   // PWCTRL1   — живлення (нема в ST7789)
    { 0xC1, 1, ILI_PWCTRL2,   0 },   // PWCTRL2
    { 0xC5, 2, ILI_VMCTRL1,   0 },   // VMCTRL1   — два аргументи
    { 0x3A, 1, ILI_COLMOD,   10 },   // COLMOD    — формат пікселя
    { 0x36, 1, ILI_MADCTL,    0 },   // MADCTL    — орієнтація (своя для ILI)
    { 0x29, 0, NULL,         20 },   // DISPON    — БЕЗ INVON: ILI його не вмикає
};
