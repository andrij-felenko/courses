int irq_num;

/* Отримання номера системного переривання */
irq_num = gpiod_to_irq(priv->irq_gpio);
if (irq_num < 0) {
    dev_err(dev, "Failed to map GPIO to IRQ: %d\n", irq_num);
    return irq_num;
}

/* Реєстрація обробника через Devres */
ret = devm_request_threaded_irq(dev, irq_num, NULL, sensor_irq_handler,
                                IRQF_TRIGGER_RISING | IRQF_ONESHOT,
                                "sensor_irq", priv);
