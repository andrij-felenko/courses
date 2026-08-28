#include <stdint.h>
#include <string.h>

// Макет структури повідомлення PARAM_SET для демонстрації
typedef struct {
    float   param_value;
    uint8_t target_system;
    uint8_t target_component;
    char    param_id[16];
    uint8_t param_type;
} mav_param_set_msg_t;

// Складання повідомлення PARAM_SET для встановлення максимальної швидкості
mav_param_set_msg_t create_param_set_float(uint8_t sys_id,
                                           uint8_t comp_id,
                                           const char *name,
                                           float val) {
    mav_param_set_msg_t msg;
    memset(&msg, 0, sizeof(msg));

    msg.target_system = sys_id;
    msg.target_component = comp_id;
    msg.param_type = 9; // MAV_PARAM_TYPE_REAL32

    // Побітове копіювання float у поле значення
    memcpy(&msg.param_value, &val, sizeof(float));

    // Безпечне копіювання імені з обмеженням 16 байтів
    strncpy(msg.param_id, name, 16);

    return msg;
}
