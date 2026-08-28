struct gpio_chip {
    const char *label;
    struct device *parent;
    int base;               /* Негативне значення для динамічної нумерації */
    u16 ngpio;              /* Кількість ліній на контролері */
    int (*request)(struct gpio_chip *gc, unsigned int offset);
    void (*free)(struct gpio_chip *gc, unsigned int offset);
    int (*get_direction)(struct gpio_chip *gc, unsigned int offset);
    int (*direction_input)(struct gpio_chip *gc, unsigned int offset);
    int (*direction_output)(struct gpio_chip *gc, unsigned int offset, int value);
    int (*get)(struct gpio_chip *gc, unsigned int offset);
    void (*set)(struct gpio_chip *gc, unsigned int offset, int value);
    void (*set_multiple)(struct gpio_chip *gc, unsigned long *mask, unsigned long *bits);
    int (*to_irq)(struct gpio_chip *gc, unsigned int offset);
    bool can_sleep;
};
