#ifndef OPTION_BYTES_H
#define OPTION_BYTES_H

#include <stdint.h>

/*
 * Конфігураційні байти як ЗНАЧЕННЯ: розкладене слово OPTR, набір правил
 * «чого писати не можна» і власне протокол запису.
 */

/* Рівень захисту від зчитування. 0xCC у переліку є навмисно: його треба вміти
   прочитати з чипа, який уже запечатали. Записати його політика не дасть. */
typedef enum {
    OPT_RDP_LEVEL0 = 0xAA,  /* відкритий доступ SWD */
    OPT_RDP_LEVEL1 = 0xBB,  /* Flash закрита для налагоджувача, зняття = Mass Erase */
    OPT_RDP_LEVEL2 = 0xCC   /* незворотне вимкнення інтерфейсу зневадження */
} opt_rdp_t;

/* Пороги детектора Brown-Out (RM0440) */
typedef enum {
    OPT_BOR_LEVEL0 = 0,  /* ~1.7 В */
    OPT_BOR_LEVEL1 = 1,  /* ~2.0 В */
    OPT_BOR_LEVEL2 = 2,  /* ~2.2 В */
    OPT_BOR_LEVEL3 = 3,  /* ~2.5 В */
    OPT_BOR_LEVEL4 = 4   /* ~2.8 В */
} opt_bor_t;

typedef enum {
    OPT_IWDG_HARDWARE = 0,  /* лічильник біжить з першого такту після живлення */
    OPT_IWDG_SOFTWARE = 1
} opt_iwdg_t;

typedef enum {
    OPT_NRST_RESERVED = 0,
    OPT_NRST_RESET_IN = 1,  /* ніжка лише приймає скидання */
    OPT_NRST_GPIO     = 2,  /* ніжка стала звичайним GPIO — рятувати нічим */
    OPT_NRST_RESET_IO = 3   /* приймає й видає скидання */
} opt_nrst_t;

typedef enum {
    OPT_BOOT_FROM_PIN = 0,  /* BOOT0 читається з ніжки: страпінг у системний завантажувач працює */
    OPT_BOOT_FIXED    = 1   /* ніжку BOOT0 вимкнено, старт завжди з користувацької Flash */
} opt_boot_t;

typedef struct {
    opt_rdp_t  rdp;
    opt_bor_t  bor;
    opt_iwdg_t iwdg;
    opt_nrst_t nrst;
    opt_boot_t boot;
} opt_config_t;

typedef enum {
    OPT_OK = 0,
    /* відмови політики — до чипа ще нічого не пішло */
    OPT_ERR_POLICY_SEAL,        /* просять записати 0xCC */
    OPT_ERR_POLICY_MASS_ERASE,  /* просять зняти захист, тобто стерти всю Flash */
    OPT_ERR_POLICY_SEALED,      /* чип уже в Level 2, писати нікуди */
    OPT_ERR_POLICY_BOR_LOW,     /* поріг BOR нижчий за потрібний робочій частоті */
    OPT_ERR_POLICY_NRST,        /* просять убити ніжку скидання */
    OPT_ERR_POLICY_BOOT,        /* просять убити страпінг BOOT0 */
    /* апаратні відмови */
    OPT_ERR_SUPPLY_LOW,         /* VDD просіла, зарядова помпа не витягне запис */
    OPT_ERR_TIMEOUT,
    OPT_ERR_UNLOCK,
    OPT_ERR_WRITE,
    OPT_ERR_VERIFY,
    OPT_ERR_RELOAD_STALLED      /* записали, але OBL_LAUNCH не скинув чип */
} opt_status_t;

/* Робоча точка плати: 170 МГц із вбудованої Flash вимагають щонайменше 2.8 В,
   тож слабший поріг BOR означає роботу на напрузі, за якої Flash уже бреше. */
#define OPT_BOR_MIN_FOR_MAX_CLOCK  OPT_BOR_LEVEL4

opt_config_t option_bytes_read(void);
uint32_t     option_bytes_encode(const opt_config_t *cfg, uint32_t optr);
int          option_bytes_equal(const opt_config_t *a, const opt_config_t *b);

/* Єдине місце, де живуть правила «як не зробити цеглинку». */
opt_status_t option_bytes_check_policy(const opt_config_t *current,
                                       const opt_config_t *wanted);

/* Повний протокол: політика → перевірка живлення → ключі → OPTSTRT → звірка →
   OBL_LAUNCH. За успіху НЕ повертається: перезавантаження опцій скидає чип. */
opt_status_t option_bytes_apply(const opt_config_t *wanted);

const char *opt_status_str(opt_status_t st);
const char *opt_rdp_str(opt_rdp_t v);
const char *opt_bor_str(opt_bor_t v);
const char *opt_iwdg_str(opt_iwdg_t v);
const char *opt_nrst_str(opt_nrst_t v);
const char *opt_boot_str(opt_boot_t v);

#endif /* OPTION_BYTES_H */
