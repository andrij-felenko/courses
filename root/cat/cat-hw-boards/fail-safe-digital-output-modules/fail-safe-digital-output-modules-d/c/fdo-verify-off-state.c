#include <stdint.h>
#include <stdbool.h>

typedef struct {
    volatile uint32_t* hs_ctrl_reg;
    volatile uint32_t* ls_ctrl_reg;
    volatile uint32_t* v_fb_hs_reg;
    volatile uint32_t* v_fb_ls_reg;
    uint32_t hs_pin_mask;
    uint32_t ls_pin_mask;
} fdo_channel_t;

typedef enum {
    FDO_OK = 0,
    FDO_ERR_HS_SHORT = 1,
    FDO_ERR_LS_SHORT = 2
} fdo_status_t;

fdo_status_t fdo_verify_off_state(const fdo_channel_t* ch) {
    /* Перевіряємо, що сигнали керування затворами вимкнені */
    *ch->hs_ctrl_reg &= ~ch->hs_pin_mask;
    *ch->ls_ctrl_reg &= ~ch->ls_pin_mask;

    /* Зчитуємо потенціали з кіл зворотного зв'язку */
    uint32_t v_hs = *ch->v_fb_hs_reg & ch->hs_pin_mask;
    uint32_t v_ls = *ch->v_fb_ls_reg & ch->ls_pin_mask;

    if (v_hs != 0) {
        /* Фіксація пробою High-Side ключа */
        return FDO_ERR_HS_SHORT;
    }

    if (v_ls != 0) {
        /* Фіксація пробою або витоку Low-Side ключа */
        return FDO_ERR_LS_SHORT;
    }

    return FDO_OK;
}
