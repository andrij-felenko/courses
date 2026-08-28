/* Отримання однієї обов'язкової лінії */
struct gpio_desc *gpiod_get(struct device *dev, const char *con_id, 
                           enum gpiod_flags flags);

/* Отримання опціональної лінії (повертає NULL замість -ENOENT) */
struct gpio_desc *gpiod_get_optional(struct device *dev, const char *con_id, 
                                     enum gpiod_flags flags);

/* Отримання лінії з масиву за індексом */
struct gpio_desc *gpiod_get_index(struct device *dev, const char *con_id, 
                                  unsigned int idx, enum gpiod_flags flags);

/* Отримання опціональної лінії за індексом */
struct gpio_desc *gpiod_get_index_optional(struct device *dev, const char *con_id, 
                                           unsigned int idx, enum gpiod_flags flags);

/* Ручне вивільнення дескриптора лінії */
void gpiod_put(struct gpio_desc *desc);
