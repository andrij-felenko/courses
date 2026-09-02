#ifndef FS_PARAMS_H
#define FS_PARAMS_H

/* Реєстр параметрів підсистеми failsafe: опис, діапазони, дефолти.
 * Імена збігаються з тими, що їх бачить оператор у PARAM_SET,
 * тому кожне мусить уміститися в 16 символів поля param_id MAVLink. */

#include <stdint.h>
#include <stdbool.h>

#define FS_PARAM_NAME_MAX 16

typedef enum {
    FS_TYPE_INT8 = 0,
    FS_TYPE_INT16,
    FS_TYPE_FLOAT
} fs_param_type_t;

/* Значення зберігаємо в тому типі, який оголошений у реєстрі:
 * прошивка порівнює int8-прапорці без плаваючої коми. */
typedef union {
    int8_t  i8;
    int16_t i16;
    float   f32;
} fs_value_t;

typedef enum {
    FS_P_THR_ENABLE = 0,
    FS_P_THR_VALUE,
    FS_P_RC_TIMEOUT,
    FS_P_RC_RECOVER,
    FS_P_GCS_TIMEOUT,
    FS_P_GCS_ENABLE,
    FS_P_EKF_THRESH,
    FS_P_GNSS_HDOP_MAX,
    FS_P_GNSS_TIMEOUT,
    FS_P_BATT_LOW_V,
    FS_P_BATT_CRIT_V,
    FS_P_BATT_HYST_MS,
    FS_P_BATT_ACT,
    FS_P_FENCE_ENABLE,
    FS_P_FENCE_RADIUS,
    FS_P_FENCE_ALT_MAX,
    FS_P_FENCE_ACT,
    FS_P_CRASH_DUMP,
    FS_P_LAST_GASP_TX,
    FS_PARAM_COUNT
} fs_param_id_t;

typedef struct {
    const char     *name;
    fs_param_type_t type;
    float           min;
    float           max;
    float           def;
    uint8_t         since;  /* версія схеми, у якій параметр з'явився */
} fs_param_desc_t;

/* Робоча копія конфігурації в ОЗП. Саме її читає ядро безпеки в реальному часі. */
typedef struct {
    fs_value_t v[FS_PARAM_COUNT];
} fs_param_block_t;

typedef enum {
    FS_PARAM_OK = 0,
    FS_PARAM_ERR_ID,      /* невідомий ідентифікатор або ім'я */
    FS_PARAM_ERR_RANGE    /* значення поза діапазоном реєстру */
} fs_param_status_t;

extern const fs_param_desc_t fs_param_desc[FS_PARAM_COUNT];

void              fs_params_load_defaults(fs_param_block_t *b);
int               fs_params_find(const char *name);  /* -1, якщо імені немає */
float             fs_params_get(const fs_param_block_t *b, fs_param_id_t id);
fs_param_status_t fs_params_set(fs_param_block_t *b, fs_param_id_t id, float value);
fs_param_status_t fs_params_set_by_name(fs_param_block_t *b, const char *name, float value);

/* Передпольотна валідація інваріантів. Повертає кількість порушень,
 * тексти складає в out (кожне з нового рядка) для видачі в STATUSTEXT. */
int fs_params_validate(const fs_param_block_t *b, float rtl_alt_m, char *out, uint32_t out_sz);

const char *fs_param_status_str(fs_param_status_t s);

#endif /* FS_PARAMS_H */
