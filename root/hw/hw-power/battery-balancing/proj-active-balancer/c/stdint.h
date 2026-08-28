#include <stdint.h>
#include <stdbool.h>

#define NCELLS        12u
#define NODES         (NCELLS + 1u)   // відводи n0..n12 між комірками

// гістерезис (на напрузі комірки біля верху заряду, де OCV крута)
#define VSTART_MV     20u             // почати, коли розкид > 20 мВ
#define VSTOP_MV       8u             // спинити, коли розкид < 8 мВ  (стоп < старт!)

// «чесне» вікно напруги
#define IPACK_MAX_MA  200             // балансуємо лише коли |струм пакета| < 200 мА

// шатл
#define SHUTTLE_HZ    25000u          // повних циклів переносу за секунду
#define DEADTIME_NS   300u            // мертвий час між фазами

typedef enum { BAL_IDLE, BAL_ACTIVE } bal_state_t;

typedef struct {
    bal_state_t state;
    uint8_t     donor;      // найповніша: звідки беремо заряд
    uint8_t     recipient;  // найпорожніша: куди кладемо
} balancer_t;

// ── нижчий рівень (реалізує драйвер плати) ──────────────────────────────
void    cellmon_read(uint16_t v_mv[NCELLS]);  // isoSPI/SPI: усі напруги, мВ
int32_t pack_current_ma(void);                // з шунта; + = заряд
bool    charger_in_cv(void);                  // зарядник тримає сталу напругу?

void    sw_set(uint8_t rail, uint8_t node, bool on);  // rail 0=верх цапа, 1=низ
void    sw_all_open(void);                    // розімкнути ВСІ ключі крос-бару
void    timer_set_hz(uint32_t hz);            // запустити ISR шатла на hz
void    timer_stop(void);
void    delay_ns(uint32_t ns);

// ── самого балансира ────────────────────────────────────────────────────
void shuttle_start(uint8_t donor, uint8_t recipient);
void shuttle_stop(void);
