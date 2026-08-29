#ifndef FM_PARAMS_H
#define FM_PARAMS_H

#include <stdint.h>

/* Таблиця параметрів автомата режимів. Усі пороги, які проза називає числами,
   живуть тут одним блоком: на борту вони приходять з енергонезалежної пам'яті
   й міняються з наземної станції, тож у коді жодного вшитого числа бути не має. */
typedef struct {
    /* Супутникова навігація */
    uint8_t  gnss_min_sats;          /* мінімум захоплених супутників          */
    uint8_t  gnss_min_fix_type;      /* 3 = 3D Fix, 4 = RTK Float, 5 = RTK Fix  */
    float    gnss_max_hdop;          /* горизонтальний фактор розмиття          */
    float    gnss_max_vdop;          /* вертикальний фактор розмиття            */

    /* Розширений фільтр Калмана: нормалізовані інновації */
    float    ekf_max_innov_pos;      /* гейт інновації положення                */
    float    ekf_max_innov_vel;      /* гейт інновації швидкості                */
    float    ekf_glitch_innov;       /* понад це — виміри взаємно суперечливі   */
    float    compass_max_yaw_err_deg;/* розбіжність компаса й гіроскопа, градуси */

    /* Джерело цілевказівок для Guided */
    uint32_t guided_timeout_ms;      /* вік останнього SET_POSITION_TARGET      */

    /* Заслінка газу */
    float    throttle_deadband;      /* зона узгодження стіка й авторегулятора   */
    float    throttle_slew_per_s;    /* межа швидкості наростання тяги, 1/с      */

    /* Детектор посадки */
    float    land_speed;             /* цільова швидкість зниження, м/с          */
    float    land_vz_epsilon;        /* |Vz|, нижче якої зниження зупинилося     */
    float    land_thr_min;           /* поріг виходу Z-регулятора, частка висіння */
    float    land_accel_var_max;     /* дисперсія акселерометра по Z             */
    uint32_t land_contact_ms;        /* витримка фази контакту з ґрунтом         */
    uint32_t land_confirm_ms;        /* витримка підтвердження посадки           */
    float    land_idle_throttle;     /* холостий хід після посадки (Spin Armed)  */

    /* Детектор польоту */
    float    in_air_alt_m;           /* висота над точкою старту                 */
    float    in_air_motor_min;       /* оберти вище холостого ходу               */
    float    in_air_accel_var_min;   /* ознака відриву за прискореннями          */

    /* Втрата зв'язку */
    uint32_t rc_loss_ms;             /* тайм-аут валідних кадрів з пульта        */
    uint32_t gcs_loss_ms;            /* тайм-аут серцебиття наземної станції     */

    /* Живлення */
    float    batt_low_cell_v;        /* Stage 1: попередження                    */
    float    batt_low_remaining;
    float    batt_crit_cell_v;       /* Stage 2: критичний рівень                */
    float    batt_crit_remaining;

    /* Геозона й повернення */
    float    fence_radius_m;
    float    fence_alt_m;
    float    rtl_alt_m;

    /* Гістерезис і перехоплення */
    uint32_t guard_stable_ms;        /* скільки охоронець мусить триматися       */
    float    pilot_override_stick;   /* відхилення стіка, що скасовує автономію  */
    float    mission_max_alt_m;      /* стеля висот у плані місії                */
} fm_params_t;

/* Значення за замовчуванням — ті самі, що названі в тексті теми. */
void fm_params_default(fm_params_t *p);

#endif /* FM_PARAMS_H */
