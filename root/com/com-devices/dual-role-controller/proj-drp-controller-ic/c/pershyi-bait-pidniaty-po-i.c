// ── Реєстри TCPCI (адреси однакові в кожного виробника) ──
#define REG_VENDOR_ID       0x00   // 2 байти
#define REG_ALERT           0x10   // 2 байти, запис-1-скидає біт
#define REG_ALERT_MASK      0x12   // 2 байти
#define REG_ROLE_CONTROL    0x1A
#define REG_POWER_CONTROL   0x1C
#define REG_CC_STATUS       0x1D
#define REG_POWER_STATUS    0x1E
#define REG_FAULT_STATUS    0x1F
#define REG_COMMAND         0x23
#define REG_VBUS_VOLTAGE    0x70   // 2 байти

// ── Значення для COMMAND ──
#define CMD_WAKE_I2C        0x11   // збудити з режиму сну
#define CMD_LOOK4CONNECTION 0x99   // запустити автономне чергування DRP

// ── ROLE_CONTROL: по 2 біти на кожен вивід CC ──
#define CC_RA   0x0
#define CC_RP   0x1
#define CC_RD   0x2
#define CC_OPEN 0x3
#define RP_DEF  0x0            // рекламований струм джерела: типовий USB
#define RP_1_5A 0x1
#define RP_3_0A 0x2
#define ROLE(drp, rp, cc2, cc1)  (((drp)<<6)|((rp)<<4)|((cc2)<<2)|(cc1))

// ── ALERT: біти подій ──
#define ALRT_CC_STATUS    (1u<<0)
#define ALRT_POWER_STATUS (1u<<1)
#define ALRT_RX_MSG       (1u<<2)
#define ALRT_FAULT        (1u<<9)

// Примітиви шини реалізує ваш драйвер I²C (адреса пристрою — зі strap ADDR):
uint8_t  r8 (uint8_t reg);
void     w8 (uint8_t reg, uint8_t val);
uint16_t r16(uint8_t reg);
void     w16(uint8_t reg, uint16_t val);

void tcpc_init(void) {
    // 0) Мертва батарея вже подбала про Rd: чип тримає стік ще до першого
    //    байта. Тому ми не поспішаємо — оживаємо спокійно.
    w8(REG_COMMAND, CMD_WAKE_I2C);

    // 1) Хто там? Санітарна перевірка присутності по VENDOR_ID.
    if (r16(REG_VENDOR_ID) == 0x0000) return;      // чипа нема — виходимо

    // 2) Скинути все, що встигло накопичитись у ALERT (запис-1-скидає).
    w16(REG_ALERT, 0xFFFF);

    // 3) Які події хочемо бачити як переривання.
    w16(REG_ALERT_MASK, ALRT_CC_STATUS | ALRT_POWER_STATUS |
                        ALRT_RX_MSG    | ALRT_FAULT);

    // 4) На старті — ні примусової, ні авто-розрядки: поки біт
    //    AutoDischargeDisconnect = 0, чипу дозволено вільно чергувати.
    w8(REG_POWER_CONTROL, 0x00);   // VCONN off, розрядка off, монітор VBUS увімк. типово

    // 5) Стати дворольовим: DRP=1, старт зі стоку на обох CC, рекламуємо 1.5 А.
    w8(REG_ROLE_CONTROL, ROLE(1, RP_1_5A, CC_RD, CC_RD));   // = 0x5A

    // 6) Пуск. Далі чип САМ гойдає Rp↔Rd й ловить партнера.
    w8(REG_COMMAND, CMD_LOOK4CONNECTION);
}
