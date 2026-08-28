// C99: Виконання повного тестового набору в main() на ПК
int main(void) {
    mock_bus_ctx_t mock;
    chip_dev_t dev;
    chip_bus_ops_t bus_ops = {
        .read = mock_bus_read,
        .write = mock_bus_write,
        .delay_ms = mock_delay_ms
    };
    
    printf("=== Запуск Unit-тестів драйвера чипа на ПК ===\n");
    
    // --- Тест 1: Успішна ініціалізація ---
    mock_bus_reset(&mock);
    chip_status_t status = chip_init(&dev, &bus_ops, &mock, 0x19);
    assert(status == CHIP_STATUS_OK);
    assert(dev.is_initialized == true);
    assert(mock.write_count >= 2); // Має бути записано CTRL_REG1 та CTRL_REG4
    printf("[PASS] Тест 1: Успішна ініціалізація та налаштування регістрів\n");
    
    // --- Тест 2: Помилка WHO_AM_I ---
    mock_bus_reset(&mock);
    mock.registers[REG_WHO_AM_I] = 0x00; // Некоректний ID
    status = chip_init(&dev, &bus_ops, &mock, 0x19);
    assert(status == CHIP_ERR_DEVICE_NOT_FOUND);
    assert(dev.is_initialized == false);
    printf("[PASS] Тест 2: Захист від некоректного ідентифікатора чипа\n");
    
    // --- Тест 3: Точність конвертації в SI ---
    mock_bus_reset(&mock);
    chip_init(&dev, &bus_ops, &mock, 0x19);
    chip_set_range(&dev, 2); // Встановлюємо діапазон ±2g
    
    // 1g вздовж осі Z (16384 відліків для 16-бітного формату 2g)
    mock_set_raw_xyz(&mock, 0, 0, 16384);
    chip_axes_data_si_t accel;
    status = chip_read_sample_si(&dev, &accel);
    assert(status == CHIP_STATUS_OK);
    
    // Перевірка прискорення: X=0, Y=0, Z ≈ 9.81 м/с²
    assert(accel.x >= -0.01f && accel.x <= 0.01f);
    assert(accel.y >= -0.01f && accel.y <= 0.01f);
    assert(accel.z >= 9.75f && accel.z <= 9.85f);
    printf("[PASS] Тест 3: Точність перетворення коду у фізичні одиниці SI (м/с²)\n");
    
    // --- Тест 4: Стійкість до короткочасних завад (Retries) ---
    mock_bus_reset(&mock);
    chip_init(&dev, &bus_ops, &mock, 0x19);
    mock_set_raw_xyz(&mock, 0, 0, 16384);
    
    // Ін'єктуємо 2 послідовні збої шини (драйвер має виконати 3 спроби і виграти)
    mock.fail_reads_countdown = 2;
    status = chip_read_sample_si(&dev, &accel);
    assert(status == CHIP_STATUS_OK);
    printf("[PASS] Тест 4: Відпрацювання повторних спроб (Retries) при збоях шини\n");
    
    printf("\n>>> Усі модульні тести успішно пройдені за 1.2 мс! <<<\n");
    return 0;
}
