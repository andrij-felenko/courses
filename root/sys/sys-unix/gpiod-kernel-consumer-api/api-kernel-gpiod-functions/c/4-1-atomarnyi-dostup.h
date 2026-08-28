/* Зчитування логічного стану лінії (1 = активний, 0 = неактивний) */
int gpiod_get_value(const struct gpio_desc *desc);

/* Встановлення логічного стану лінії */
void gpiod_set_value(struct gpio_desc *desc, int value);

/* Зчитування фізичного електричного рівня (ігнорує прапор ACTIVE_LOW) */
int gpiod_get_raw_value(const struct gpio_desc *desc);

/* Встановлення фізичного електричного рівня (ігнорує прапор ACTIVE_LOW) */
void gpiod_set_raw_value(struct gpio_desc *desc, int value);
