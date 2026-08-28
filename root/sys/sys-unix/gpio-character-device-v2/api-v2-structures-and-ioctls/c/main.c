struct gpio_v2_line_attribute {
    __u32 id;           /* Ідентифікатор атрибута (GPIO_V2_LINE_ATTR_ID_*) */
    __u32 padding;
    union {
        __u64 flags;                /* Нові прапори, якщо id == ATTR_ID_FLAGS */
        __u64 values;               /* Логічні значення, якщо id == ATTR_ID_OUTPUT_VALUES */
        __u32 debounce_period_us;   /* Період придушення брязкоту в мкс, якщо ATTR_ID_DEBOUNCE */
    };
};

struct gpio_v2_line_config_attribute {
    struct gpio_v2_line_attribute attr; /* Сам атрибут */
    __u64 mask;                         /* Маска ліній з offsets[], до яких він застосовується */
};
