struct gpio_descs *data_bus;

/* Отримання масиву ліній "data-gpios" з Device Tree */
data_bus = devm_gpiod_get_array(dev, "data", GPIOD_OUT_LOW);
if (IS_ERR(data_bus))
    return PTR_ERR(data_bus);

/* Кількість отриманих ліній зберігається у data_bus->ndescs */
unsigned long values = 0xA5; // Бінарне 10100101

/* Атомарне встановлення значення всього масиву за один виклик */
gpiod_set_array_value(data_bus->ndescs, data_bus->desc, data_bus->info, &values);
