#include "option_bytes.h"
#include "stm32g4_regs.h"

/*
 * Сценарій випуску: прошивка на вже змонтованій платі один раз доводить
 * Option Bytes до потрібного стану. Усе, що вона друкує, іде в ITM — канал,
 * який лишається доступним рівно доти, доки живий налагоджувач.
 */

static void trace_char(char c)
{
    uint32_t guard = 100000UL;

    /* Без підключеного налагоджувача ITM не приймає нічого, і чекати на
       готовність порту означало б зависнути назавжди. */
    if ((CORE_DEMCR & CORE_DEMCR_TRCENA) == 0UL) {
        return;
    }
    if ((ITM_TER & 1UL) == 0UL) {
        return;
    }

    while (ITM_STIM0_U32 == 0UL) {
        if (--guard == 0UL) {
            return;
        }
    }
    ITM_STIM0_U8 = (uint8_t)c;
}

static void trace(const char *text)
{
    while (*text != '\0') {
        trace_char(*text++);
    }
}

static void trace_hex32(uint32_t value)
{
    static const char digits[] = "0123456789ABCDEF";
    int shift;

    trace("0x");
    for (shift = 28; shift >= 0; shift -= 4) {
        trace_char(digits[(value >> shift) & 0xFUL]);
    }
}

static void trace_config(const char *label, const opt_config_t *cfg)
{
    trace(label);
    trace(": ");
    trace(opt_rdp_str(cfg->rdp));   trace(" | ");
    trace(opt_bor_str(cfg->bor));   trace(" | ");
    trace(opt_iwdg_str(cfg->iwdg)); trace(" | ");
    trace(opt_nrst_str(cfg->nrst)); trace(" | ");
    trace(opt_boot_str(cfg->boot));
    trace("\n");
}

int main(void)
{
    opt_config_t current;
    opt_status_t status;

    /* Цільова конфігурація серійного виробу. Кожне поле тут — це рішення,
       яке в разі помилки коштує партії плат. */
    static const opt_config_t wanted = {
        .rdp  = OPT_RDP_LEVEL1,     /* прошивку закрито, чип іще можна стерти */
        .bor  = OPT_BOR_LEVEL4,     /* 2.8 В: нижче Flash бреше на 170 МГц */
        .iwdg = OPT_IWDG_SOFTWARE,  /* апаратний старт WDG зациклив би довгу ініціалізацію */
        .nrst = OPT_NRST_RESET_IO,  /* ніжка скидання лишається скиданням */
        .boot = OPT_BOOT_FROM_PIN   /* страпінг у системний завантажувач лишається */
    };

    trace("\n== Option Bytes ==\n");
    trace("сире слово OPTR: ");
    trace_hex32(FLASH->OPTR);
    trace("\n");

    current = option_bytes_read();
    trace_config("поточна", &current);
    trace_config("бажана ", &wanted);

    if (option_bytes_equal(&current, &wanted)) {
        /* Службова сторінка має свій ресурс перезапису, та й кожен зайвий
           запис — це ще один шанс спіймати просідання живлення. */
        trace("збіг: у Flash не пишемо нічого\n");
    } else {
        status = option_bytes_apply(&wanted);
        /* Успішний шлях сюди не повертається — чип уже перезавантажився. */
        trace("не застосовано: ");
        trace(opt_status_str(status));
        trace("\n");
    }

    /* Свідомо не йдемо ні в сон, ні в переналаштування PA13/PA14: саме ці
       два рухи в перших рядках main() і залишають ST-Link без відповіді. */
    for (;;) {
    }
}
