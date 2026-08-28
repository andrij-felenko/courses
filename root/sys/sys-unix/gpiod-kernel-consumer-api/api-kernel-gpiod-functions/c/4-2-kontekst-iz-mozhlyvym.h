/* Зчитування логічного стану лінії з можливістю сну */
int gpiod_get_value_cansleep(const struct gpio_desc *desc);

/* Встановлення логічного стану лінії з можливістю сну */
void gpiod_set_value_cansleep(struct gpio_desc *desc, int value);

/* Зчитування фізичного рівня з можливістю сну */
int gpiod_get_raw_value_cansleep(const struct gpio_desc *desc);

/* Встановлення фізичного рівня з можливістю сну */
void gpiod_set_raw_value_cansleep(struct gpio_desc *desc, int value);
