/* Отримання та автоматична активація тактового сигналу */
chip->clk = devm_clk_get_enabled(&pdev->dev, "bus_clk");
if (IS_ERR(chip->clk))
	return dev_err_probe(&pdev->dev, PTR_ERR(chip->clk),
	                      "Не вдалося активувати тактування\n");

/* Отримання та ввімкнення лінії живлення */
ret = devm_regulator_get_enable(&pdev->dev, "vdd");
if (ret)
	return dev_err_probe(&pdev->dev, ret, "Помилка живлення VDD\n");

/* Отримання дескриптора скидання GPIO */
chip->reset_gpio = devm_gpiod_get_optional(&pdev->dev, "reset", GPIOD_OUT_LOW);
if (IS_ERR(chip->reset_gpio))
	return PTR_ERR(chip->reset_gpio);
