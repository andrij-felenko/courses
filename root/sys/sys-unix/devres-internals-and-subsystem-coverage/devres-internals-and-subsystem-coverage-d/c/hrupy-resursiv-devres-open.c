void *group_id;

/* Відкриваємо ізольовану групу ресурсів */
group_id = devres_open_group(&pdev->dev, NULL, GFP_KERNEL);
if (!group_id)
	return -ENOMEM;

/* Усі виклики devm_* нижче додаються всередину цієї групи */
temp_buf = devm_kmalloc(&pdev->dev, 4096, GFP_KERNEL);
if (!temp_buf) {
	/* Відкочуємо виключно ресурси цієї групи */
	devres_release_group(&pdev->dev, group_id);
	return -ENOMEM;
}

ret = acme_run_calibration(&pdev->dev, temp_buf);
if (ret) {
	/* Помилка калібрування: звільняємо лише тимчасовий буфер */
	devres_release_group(&pdev->dev, group_id);
	return ret;
}

/* Калібрування успішне: закриваємо групу (ресурси лишаються активними) */
devres_close_group(&pdev->dev, group_id);
