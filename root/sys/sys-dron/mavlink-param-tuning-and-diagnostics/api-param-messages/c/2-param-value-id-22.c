/* Бінарна структура повідомлення PARAM_VALUE */
typedef struct __mavlink_param_value_t {
    float    param_value;   /* 4 байти значення */
    uint16_t param_count;   /* загальна кількість параметрів */
    uint16_t param_index;   /* індекс поточного параметра */
    char     param_id[16];  /* 16-байтний ідентифікатор */
    uint8_t  param_type;    /* тип даних (MAV_PARAM_TYPE) */
} mavlink_param_value_t;

/* Безпечне копіювання ідентифікатора у нуль-термінований рядок */
void extract_safe_param_id(const char wire_id[16], char out_str[17]) {
    memcpy(out_str, wire_id, 16);
    out_str[16] = '\0';
}
