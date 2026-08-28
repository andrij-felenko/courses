struct gpio_desc *reset_gpio;

reset_gpio = devm_gpiod_get(dev, "reset", GPIOD_OUT_LOW);
if (IS_ERR(reset_gpio)) {
    int err = PTR_ERR(reset_gpio);
    
    if (err == -EPROBE_DEFER) {
        /* Контролер GPIO ще не ініціалізовано, чекаємо повторної спроби */
        return -EPROBE_DEFER;
    }
    
    dev_err(dev, "Failed to get reset GPIO: %d\n", err);
    return err;
}
