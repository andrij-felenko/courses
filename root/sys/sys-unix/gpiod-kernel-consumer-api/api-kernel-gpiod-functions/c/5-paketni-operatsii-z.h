struct gpio_descs {
    unsigned int ndescs;
    struct gpio_desc *desc[];
};

/* Отримання групи ліній з Device Tree */
struct gpio_descs *gpiod_get_array(struct device *dev, const char *con_id, 
                                   enum gpiod_flags flags);

struct gpio_descs *devm_gpiod_get_array(struct device *dev, const char *con_id, 
                                        enum gpiod_flags flags);

/* Одночасне встановлення значень для масиву ліній */
void gpiod_set_array_value(unsigned int array_size, 
                           struct gpio_desc **desc_array,
                           struct gpio_array *array_info, 
                           unsigned long *value_bitmap);

/* Пакетне встановлення значень для розширювачів I2C/SPI з сном */
void gpiod_set_array_value_cansleep(unsigned int array_size, 
                                    struct gpio_desc **desc_array,
                                    struct gpio_array *array_info, 
                                    unsigned long *value_bitmap);
