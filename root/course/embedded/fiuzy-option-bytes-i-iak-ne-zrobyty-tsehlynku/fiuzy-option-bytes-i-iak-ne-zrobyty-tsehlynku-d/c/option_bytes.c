#include "option_bytes.h"
#include "stm32g4_regs.h"
#include "supply_guard.h"

/* Скільки холостих обертів чекаємо зняття BSY. Запис службової сторінки
   триває одиниці мілісекунд; мільйон обертів — це із запасом на будь-якій
   частоті ядра, і водночас гарантія, що ми не зависнемо назавжди. */
#define FLASH_TIMEOUT_LOOPS  1000000UL

/* Поріг PVD, нижче якого запис Option Bytes не починаємо: зарядова помпа
   на просілій шині не проштовхне заряд крізь діелектрик затвора, і комірка
   лишиться в проміжному стані — рівно сценарій 5. */
#define SUPPLY_WRITE_THRESHOLD  SUPPLY_PVD_2V9

static int flash_wait_ready(void)
{
    uint32_t guard = FLASH_TIMEOUT_LOOPS;

    while ((FLASH->SR & FLASH_SR_BSY) != 0UL) {
        if (--guard == 0UL) {
            return 0;
        }
    }
    return 1;
}

static void flash_clear_errors(void)
{
    /* прапорці помилок скидаються записом одиниці */
    FLASH->SR = FLASH_SR_ERRORS | FLASH_SR_EOP;
}

static int flash_unlock(void)
{
    /* Крок 1: знімаємо LOCK з основного контролера. Поки він стоїть,
       OPTLOCK не знімається взагалі. */
    if ((FLASH->CR & FLASH_CR_LOCK) != 0UL) {
        FLASH->KEYR = FLASH_KEY1;
        FLASH->KEYR = FLASH_KEY2;
        if ((FLASH->CR & FLASH_CR_LOCK) != 0UL) {
            return 0;
        }
    }

    /* Крок 2: окремі ключі на сектор Option Bytes. */
    if ((FLASH->CR & FLASH_CR_OPTLOCK) != 0UL) {
        FLASH->OPTKEYR = FLASH_OPTKEY1;
        FLASH->OPTKEYR = FLASH_OPTKEY2;
        if ((FLASH->CR & FLASH_CR_OPTLOCK) != 0UL) {
            return 0;
        }
    }
    return 1;
}

static void flash_lock(void)
{
    FLASH->CR |= FLASH_CR_OPTLOCK;
    FLASH->CR |= FLASH_CR_LOCK;
}

opt_config_t option_bytes_read(void)
{
    const uint32_t optr = FLASH->OPTR;
    const uint8_t  rdp  = (uint8_t)(optr & FLASH_OPTR_RDP_MSK);
    opt_config_t   cfg;

    /* Будь-яке значення, крім 0xAA і 0xCC, апаратно означає Level 1.
       Нормалізуємо його до 0xBB, інакше порівняння «те саме?» брехало б
       і ми переписували б службову сторінку без потреби. */
    if (rdp == (uint8_t)OPT_RDP_LEVEL0) {
        cfg.rdp = OPT_RDP_LEVEL0;
    } else if (rdp == (uint8_t)OPT_RDP_LEVEL2) {
        cfg.rdp = OPT_RDP_LEVEL2;
    } else {
        cfg.rdp = OPT_RDP_LEVEL1;
    }

    cfg.bor  = (opt_bor_t)((optr & FLASH_OPTR_BOR_MSK) >> FLASH_OPTR_BOR_POS);
    cfg.iwdg = ((optr & FLASH_OPTR_IWDG_SW) != 0UL) ? OPT_IWDG_SOFTWARE : OPT_IWDG_HARDWARE;
    cfg.nrst = (opt_nrst_t)((optr & FLASH_OPTR_NRST_MSK) >> FLASH_OPTR_NRST_POS);
    cfg.boot = ((optr & FLASH_OPTR_NSWBOOT0) != 0UL) ? OPT_BOOT_FROM_PIN : OPT_BOOT_FIXED;

    return cfg;
}

uint32_t option_bytes_encode(const opt_config_t *cfg, uint32_t optr)
{
    /* Чужі поля (WWDG_SW, nRST_STOP, DBANK, PCROP…) не чіпаємо: у службовому
       слові вони теж живуть, і сліпе обнулення поламало б чужі налаштування. */
    optr &= ~(FLASH_OPTR_RDP_MSK | FLASH_OPTR_BOR_MSK |
              FLASH_OPTR_IWDG_SW | FLASH_OPTR_NRST_MSK);

    optr |= (uint32_t)cfg->rdp & FLASH_OPTR_RDP_MSK;
    optr |= ((uint32_t)cfg->bor << FLASH_OPTR_BOR_POS) & FLASH_OPTR_BOR_MSK;
    optr |= ((uint32_t)cfg->nrst << FLASH_OPTR_NRST_POS) & FLASH_OPTR_NRST_MSK;

    if (cfg->iwdg == OPT_IWDG_SOFTWARE) {
        optr |= FLASH_OPTR_IWDG_SW;
    }

    if (cfg->boot == OPT_BOOT_FROM_PIN) {
        /* nBOOT0 у цьому режимі не має значення — лишаємо як було */
        optr |= FLASH_OPTR_NSWBOOT0;
    } else {
        optr &= ~FLASH_OPTR_NSWBOOT0;
        optr |= FLASH_OPTR_NBOOT0;
    }

    return optr;
}

int option_bytes_equal(const opt_config_t *a, const opt_config_t *b)
{
    return (a->rdp  == b->rdp)  &&
           (a->bor  == b->bor)  &&
           (a->iwdg == b->iwdg) &&
           (a->nrst == b->nrst) &&
           (a->boot == b->boot);
}

opt_status_t option_bytes_check_policy(const opt_config_t *current,
                                       const opt_config_t *wanted)
{
    /* Чип уже запечатано: інтерфейс зневадження вимкнено апаратно, і навіть
       якби ми щось записали, перевірити це не було б чим. */
    if (current->rdp == OPT_RDP_LEVEL2) {
        return OPT_ERR_POLICY_SEALED;
    }

    /* Level 2 — односпрямований перехід. З прошивки його не роблять НІКОЛИ:
       помилка в оновленні після цього означає утилізацію плати. */
    if (wanted->rdp == OPT_RDP_LEVEL2) {
        return OPT_ERR_POLICY_SEAL;
    }

    /* Зняття захисту тягне за собою Mass Erase — тобто стирання коду, який
       саме зараз виконується. Це робота програматора, а не прошивки. */
    if (current->rdp != OPT_RDP_LEVEL0 && wanted->rdp == OPT_RDP_LEVEL0) {
        return OPT_ERR_POLICY_MASS_ERASE;
    }

    if (wanted->bor < OPT_BOR_MIN_FOR_MAX_CLOCK) {
        return OPT_ERR_POLICY_BOR_LOW;
    }

    /* Без робочої ніжки скидання не працює Connect Under Reset — головний
       спосіб перехопити ядро до того, як прошивка вимкне SWD. */
    if (wanted->nrst == OPT_NRST_GPIO || wanted->nrst == OPT_NRST_RESERVED) {
        return OPT_ERR_POLICY_NRST;
    }

    /* Живий страпінг BOOT0 — другий шлях порятунку: старт у системний
       завантажувач в обхід пошкодженого користувацького коду. */
    if (wanted->boot == OPT_BOOT_FIXED) {
        return OPT_ERR_POLICY_BOOT;
    }

    return OPT_OK;
}

opt_status_t option_bytes_apply(const opt_config_t *wanted)
{
    opt_config_t current = option_bytes_read();
    opt_config_t written;
    opt_status_t policy;
    int supply_ok;

    policy = option_bytes_check_policy(&current, wanted);
    if (policy != OPT_OK) {
        return policy;
    }

    supply_guard_enable(SUPPLY_WRITE_THRESHOLD);
    supply_ok = supply_guard_above_threshold();
    supply_guard_disable();
    if (!supply_ok) {
        return OPT_ERR_SUPPLY_LOW;
    }

    if (!flash_wait_ready()) {
        return OPT_ERR_TIMEOUT;
    }
    flash_clear_errors();

    if (!flash_unlock()) {
        flash_lock();
        return OPT_ERR_UNLOCK;
    }

    FLASH->OPTR = option_bytes_encode(wanted, FLASH->OPTR);
    FLASH->CR |= FLASH_CR_OPTSTRT;

    if (!flash_wait_ready()) {
        flash_lock();
        return OPT_ERR_TIMEOUT;
    }

    if ((FLASH->SR & FLASH_SR_ERRORS) != 0UL) {
        flash_clear_errors();
        flash_lock();
        return OPT_ERR_WRITE;
    }
    FLASH->SR = FLASH_SR_EOP;

    /* Звірка: у слові OPTR має стояти рівно те, що ми туди клали. Розбіжність
       означає напівзаписану комірку — далі йти не можна. */
    written = option_bytes_read();
    if (!option_bytes_equal(&written, wanted)) {
        flash_lock();
        return OPT_ERR_VERIFY;
    }

    /* OBL_LAUNCH пишеться лише поки OPTLOCK знятий, тому блокування — ПІСЛЯ.
       Успішний запис звідси не повертається: перезавантаження опцій скидає
       чип, і наступний рядок виконується вже після нового старту. */
    FLASH->CR |= FLASH_CR_OBL_LAUNCH;

    for (volatile uint32_t spin = 0; spin < FLASH_TIMEOUT_LOOPS; ++spin) {
    }

    flash_lock();
    return OPT_ERR_RELOAD_STALLED;
}

const char *opt_status_str(opt_status_t st)
{
    switch (st) {
    case OPT_OK:                    return "ok";
    case OPT_ERR_POLICY_SEAL:       return "політика: запис RDP Level 2 незворотний";
    case OPT_ERR_POLICY_MASS_ERASE: return "політика: зняття захисту стерло б усю Flash";
    case OPT_ERR_POLICY_SEALED:     return "політика: чип уже в Level 2";
    case OPT_ERR_POLICY_BOR_LOW:    return "політика: поріг BOR замалий для робочої частоти";
    case OPT_ERR_POLICY_NRST:       return "політика: ніжка скидання мусить лишитися скиданням";
    case OPT_ERR_POLICY_BOOT:       return "політика: страпінг BOOT0 мусить лишитися живим";
    case OPT_ERR_SUPPLY_LOW:        return "живлення: VDD нижче порога запису";
    case OPT_ERR_TIMEOUT:           return "контролер Flash не звільнив BSY";
    case OPT_ERR_UNLOCK:            return "ключі не зняли блокування";
    case OPT_ERR_WRITE:             return "апаратна помилка запису";
    case OPT_ERR_VERIFY:            return "записане не збіглося з бажаним";
    case OPT_ERR_RELOAD_STALLED:    return "записано, але OBL_LAUNCH не скинув чип";
    default:                        return "невідомий стан";
    }
}

const char *opt_rdp_str(opt_rdp_t v)
{
    switch (v) {
    case OPT_RDP_LEVEL0: return "Level 0 (0xAA)";
    case OPT_RDP_LEVEL1: return "Level 1";
    case OPT_RDP_LEVEL2: return "Level 2 (0xCC)";
    default:             return "?";
    }
}

const char *opt_bor_str(opt_bor_t v)
{
    switch (v) {
    case OPT_BOR_LEVEL0: return "BOR 0 (~1.7 В)";
    case OPT_BOR_LEVEL1: return "BOR 1 (~2.0 В)";
    case OPT_BOR_LEVEL2: return "BOR 2 (~2.2 В)";
    case OPT_BOR_LEVEL3: return "BOR 3 (~2.5 В)";
    case OPT_BOR_LEVEL4: return "BOR 4 (~2.8 В)";
    default:             return "BOR ?";
    }
}

const char *opt_iwdg_str(opt_iwdg_t v)
{
    return (v == OPT_IWDG_SOFTWARE) ? "IWDG програмний" : "IWDG апаратний";
}

const char *opt_nrst_str(opt_nrst_t v)
{
    switch (v) {
    case OPT_NRST_RESET_IN: return "NRST вхід скидання";
    case OPT_NRST_GPIO:     return "NRST як GPIO";
    case OPT_NRST_RESET_IO: return "NRST вхід/вихід скидання";
    default:                return "NRST зарезервовано";
    }
}

const char *opt_boot_str(opt_boot_t v)
{
    return (v == OPT_BOOT_FROM_PIN) ? "BOOT0 з ніжки" : "BOOT0 з опції";
}
