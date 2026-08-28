#include <stdint.h>
#include <stdbool.h>

/* Базові адреси регістрів MII (IEEE 802.3 Clause 22) */
#define MII_BMCR            0x00
#define MII_BMSR            0x01
#define MII_ANAR            0x04
#define MII_ANLPAR          0x05
#define MII_ANER            0x06
#define MII_1000CR          0x09
#define MII_1000SR          0x0A

/* Бітові маски BMCR (Регістр 0) */
#define BMCR_RESET          (1u << 15)
#define BMCR_AN_ENABLE      (1u << 12)
#define BMCR_RESTART_AN     (1u << 9)

/* Бітові маски BMSR (Регістр 1) */
#define BMSR_AN_COMPLETE    (1u << 5)
#define BMSR_LINK_STATUS    (1u << 2)

/* Бітові маски ANAR / ANLPAR (Регістри 4 та 5) */
#define ADVERTISE_10HALF    (1u << 5)
#define ADVERTISE_10FULL    (1u << 6)
#define ADVERTISE_100HALF   (1u << 7)
#define ADVERTISE_100FULL   (1u << 8)
#define ADVERTISE_PAUSE     (1u << 10)
#define ADVERTISE_ASYM_PAUSE (1u << 11)

/* Бітові маски 1000CR / 1000SR (Регістри 9 та 10) */
#define ADVERTISE_1000HALF  (1u << 8)
#define ADVERTISE_1000FULL  (1u << 9)
#define STATUS_1000HALF     (1u << 10)
#define STATUS_1000FULL     (1u << 11)
#define STATUS_MS_FAULT     (1u << 15)
#define STATUS_MS_RESULT    (1u << 14) /* 1 = Master, 0 = Slave */

/* Бітові маски ANER (Регістр 6) */
#define ANER_LP_AN_ABLE     (1u << 0)
#define ANER_PAGE_RX        (1u << 1)

typedef enum {
    SPEED_UNKNOWN = 0,
    SPEED_10MBPS  = 10,
    SPEED_100MBPS = 100,
    SPEED_1000MBPS = 1000
} eth_speed_t;

typedef enum {
    DUPLEX_HALF = 0,
    DUPLEX_FULL = 1
} eth_duplex_t;

typedef enum {
    CLOCK_SLAVE = 0,
    CLOCK_MASTER = 1
} eth_clock_role_t;

typedef struct {
    eth_speed_t speed;
    eth_duplex_t duplex;
    eth_clock_role_t clock_role;
    bool pause_tx;
    bool pause_rx;
    bool parallel_detection_used;
    bool duplex_mismatch_warning;
} eth_link_result_t;

/* Прототипи апаратного доступу до шини MDIO */
uint16_t mdio_read(uint8_t phy_addr, uint8_t reg_addr);
void mdio_write(uint8_t phy_addr, uint8_t reg_addr, uint16_t val);
void delay_ms(uint32_t ms);

/* Ініціалізація та перезапуск переговорів */
bool phy_start_auto_negotiation(uint8_t phy_addr) {
    /* 1. Налаштовуємо рекламовані можливості (10/100M + PAUSE) */
    uint16_t anar = ADVERTISE_10HALF | ADVERTISE_10FULL |
                    ADVERTISE_100HALF | ADVERTISE_100FULL |
                    ADVERTISE_PAUSE | ADVERTISE_ASYM_PAUSE | 0x0001; /* 802.3 Selector */
    mdio_write(phy_addr, MII_ANAR, anar);

    /* 2. Налаштовуємо гігабітні можливості (1000BASE-T Full) */
    uint16_t gcr = ADVERTISE_1000FULL;
    mdio_write(phy_addr, MII_1000CR, gcr);

    /* 3. Увімкнення та примусовий перезапуск Auto-Negotiation */
    uint16_t bmcr = mdio_read(phy_addr, MII_BMCR);
    bmcr |= (BMCR_AN_ENABLE | BMCR_RESTART_AN);
    mdio_write(phy_addr, MII_BMCR, bmcr);

    return true;
}

/* Опитування завершення та арбітраж результату */
bool phy_poll_and_resolve(uint8_t phy_addr, uint32_t timeout_ms, eth_link_result_t *out_res) {
    uint32_t elapsed = 0;
    bool an_complete = false;

    while (elapsed < timeout_ms) {
        uint16_t bmsr = mdio_read(phy_addr, MII_BMSR);
        
        /* Читаємо повторно для скидання засувки Latching Low */
        if (bmsr & BMSR_LINK_STATUS) {
            bmsr = mdio_read(phy_addr, MII_BMSR);
            if ((bmsr & BMSR_LINK_STATUS) && (bmsr & BMSR_AN_COMPLETE)) {
                an_complete = true;
                break;
            }
        }
        delay_ms(50);
        elapsed += 50;
    }

    if (!an_complete) {
        return false; /* Таймаут переговорів або відсутній фізичний сигнал */
    }

    /* Зчитуємо результати обміну */
    uint16_t anlpar = mdio_read(phy_addr, MII_ANLPAR);
    uint16_t aner   = mdio_read(phy_addr, MII_ANER);
    uint16_t gsr    = mdio_read(phy_addr, MII_1000SR);
    uint16_t gcr    = mdio_read(phy_addr, MII_1000CR);
    uint16_t anar   = mdio_read(phy_addr, MII_ANAR);

    /* Перевірка помилки конфігурації Master/Slave */
    if (gsr & STATUS_MS_FAULT) {
        return false; /* Конфлікт тактування Master/Slave */
    }

    out_res->parallel_detection_used = !(aner & ANER_LP_AN_ABLE);
    out_res->duplex_mismatch_warning = false;

    /* Пріоритет 1: 1000BASE-T Full-Duplex */
    if ((gcr & ADVERTISE_1000FULL) && (gsr & STATUS_1000FULL)) {
        out_res->speed = SPEED_1000MBPS;
        out_res->duplex = DUPLEX_FULL;
        out_res->clock_role = (gsr & STATUS_MS_RESULT) ? CLOCK_MASTER : CLOCK_SLAVE;
    }
    /* Пріоритет 2: 1000BASE-T Half-Duplex */
    else if ((gcr & ADVERTISE_1000HALF) && (gsr & STATUS_1000HALF)) {
        out_res->speed = SPEED_1000MBPS;
        out_res->duplex = DUPLEX_HALF;
        out_res->clock_role = (gsr & STATUS_MS_RESULT) ? CLOCK_MASTER : CLOCK_SLAVE;
    }
    /* Пріоритет 3: 100BASE-TX Full-Duplex */
    else if ((anar & ADVERTISE_100FULL) && (anlpar & ADVERTISE_100FULL)) {
        out_res->speed = SPEED_100MBPS;
        out_res->duplex = DUPLEX_FULL;
    }
    /* Пріоритет 4: 100BASE-TX Half-Duplex */
    else if ((anar & ADVERTISE_100HALF) && (anlpar & ADVERTISE_100HALF)) {
        out_res->speed = SPEED_100MBPS;
        out_res->duplex = DUPLEX_HALF;
        if (out_res->parallel_detection_used) {
            out_res->duplex_mismatch_warning = true;
        }
    }
    /* Пріоритет 5: 10BASE-T Full-Duplex */
    else if ((anar & ADVERTISE_10FULL) && (anlpar & ADVERTISE_10FULL)) {
        out_res->speed = SPEED_10MBPS;
        out_res->duplex = DUPLEX_FULL;
    }
    /* Пріоритет 6: 10BASE-T Half-Duplex */
    else if ((anar & ADVERTISE_10HALF) && (anlpar & ADVERTISE_10HALF)) {
        out_res->speed = SPEED_10MBPS;
        out_res->duplex = DUPLEX_HALF;
        if (out_res->parallel_detection_used) {
            out_res->duplex_mismatch_warning = true;
        }
    } else {
        return false; /* Немає спільних режимів */
    }

    /* Розв'язання симетричного/асиметричного керування потоком PAUSE */
    bool loc_pause = (anar & ADVERTISE_PAUSE) != 0;
    bool loc_asym  = (anar & ADVERTISE_ASYM_PAUSE) != 0;
    bool rem_pause = (anlpar & ADVERTISE_PAUSE) != 0;
    bool rem_asym  = (anlpar & ADVERTISE_ASYM_PAUSE) != 0;

    out_res->pause_tx = (loc_pause && rem_pause) || (loc_asym && rem_pause && rem_asym);
    out_res->pause_rx = (loc_pause && rem_pause) || (loc_pause && loc_asym && rem_asym);

    return true;
}
