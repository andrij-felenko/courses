struct gpio_desc *devm_gpiod_get(struct device *dev, const char *con_id, 
                                 enum gpiod_flags flags);

struct gpio_desc *devm_gpiod_get_optional(struct device *dev, const char *con_id, 
                                          enum gpiod_flags flags);

struct gpio_desc *devm_gpiod_get_index(struct device *dev, const char *con_id, 
                                       unsigned int idx, enum gpiod_flags flags);

struct gpio_desc *devm_gpiod_get_index_optional(struct device *dev, const char *con_id, 
                                                unsigned int idx, enum gpiod_flags flags);

void devm_gpiod_put(struct device *dev, struct gpio_desc *desc);
