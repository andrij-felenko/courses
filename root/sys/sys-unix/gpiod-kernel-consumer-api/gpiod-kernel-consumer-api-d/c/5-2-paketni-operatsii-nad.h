struct gpio_descs *bus_gpios;

/* Отримання групи ліній з Device Tree (data-gpios = <&gpio1 0 ...>, <&gpio1 1 ...>) */
bus_gpios = devm_gpiod_get_array(dev, "data", GPIOD_OUT_LOW);
if (IS_ERR(bus_gpios))
    return PTR_ERR(bus_gpios);

/* Одночасне встановлення значень для всього масиву */
DECLARE_BITMAP(values, 8);
values[0] = 0xAB; /* 8-бітне значення для шини */

gpiod_set_array_value(bus_gpios->ndescs, bus_gpios->desc, NULL, values);
