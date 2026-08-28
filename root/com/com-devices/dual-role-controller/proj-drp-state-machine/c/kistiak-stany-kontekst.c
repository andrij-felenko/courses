#include <stdint.h>
#include <stdbool.h>

// ── Стани під'єднання (карта вище) ───────────────────────────────
typedef enum {
    TC_UNATTACHED,        // гойдалка Rp<->Rd, чекаємо партнера
    TC_ATTACHWAIT_SNK,    // бачимо джерело — відлежуємо (дебаунс)
    TC_ATTACHWAIT_SRC,    // бачимо стік — відлежуємо
    TC_ATTACHED_SNK,      // ми СТІК: споживаємо VBUS
    TC_ATTACHED_SRC,      // ми ДЖЕРЕЛО: жену VBUS
    TC_TRY_SRC,           // вподобання: наполягаємо стати джерелом
    TC_TRYWAIT_SNK,       // Try не вигорів — поступаємось у стік
    TC_ERROR_RECOVERY,    // аварійний скид: усе off, CC=Open
} tc_state_t;

// Що МИ виставляємо на CC
typedef enum { CC_PULL_OPEN, CC_PULL_RP, CC_PULL_RD } cc_pull_t;

// Що ми БАЧИМО на CC (залізо тлумачить відносно нашої підтяжки):
//  RD_PARTNER — ми на Rp і бачимо чужий Rd => партнер СТІК
//  RP_PARTNER — ми на Rd і бачимо чужий Rp => партнер ДЖЕРЕЛО
typedef enum { CC_OPEN, CC_RD_PARTNER, CC_RP_PARTNER } cc_seen_t;

// Під-стани обміну ролі (PR_Swap)
typedef enum {
    SWAP_IDLE,
    SWAP_WAIT_ACCEPT,     // надіслали PR_Swap, чекаємо Accept
    SWAP_SRC_OFF,         // були джерелом: гасимо VBUS до vSafe0V
    SWAP_WAIT_PSRDY,      // були стоком: чекаємо PS_RDY від джерела
    SWAP_SRC_ON,          // ми новий: піднімаємо VBUS до vSafe5V
} swap_state_t;

typedef struct {
    tc_state_t  state;
    uint32_t    t_enter;      // мітка часу входу в стан, мс
    // гойдалка DRP
    uint32_t    t_toggle;     // коли востаннє перемкнули підтяжку
    bool        show_rp;      // фаза гойдалки: зараз показуємо Rp?
    // дебаунс краю CC
    cc_seen_t   cc_last;
    uint32_t    t_cc_edge;    // відколи CC тримає поточне значення
    // конфіг
    bool        try_src;      // вподобання Try.SRC увімкнене?
    // обмін ролі
    swap_state_t swap;
    uint32_t    t_swap;       // таймер поточного кроку обміну
} port_t;
