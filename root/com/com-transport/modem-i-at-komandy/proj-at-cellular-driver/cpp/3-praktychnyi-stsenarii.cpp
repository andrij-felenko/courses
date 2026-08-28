void modem_bringup_example_cpp(CellularAtDriver& driver) {
    /* 1. Реєстрація лямбда-обробників спонтанних подій URC */
    driver.register_urc("+CEREG:", [](std::string_view line) {
        std::cout << "[EVENT CPP] Зміна статусу реєстрації LTE: " << line << "\n";
    });

    driver.register_urc("+QIURC: \"recv\"", [](std::string_view line) {
        std::cout << "[EVENT CPP] Отримано вхідний сокетний пакет: " << line << "\n";
    });

    /* 2. Синхронізація з модемом */
    auto echo_resp = driver.send_command("ATE0", std::chrono::milliseconds(1000));
    if (!echo_resp.has_value()) {
        std::cerr << "[ERROR CPP] Модем не відповідає на UART!\n";
        return;
    }

    /* 3. Увімкнення детальних помилок */
    driver.send_command("AT+CMEE=2", std::chrono::milliseconds(1000));

    /* 4. Запит якості сигналу */
    if (auto csq_resp = driver.send_command("AT+CSQ", std::chrono::milliseconds(1000))) {
        std::cout << "[MODEM CPP] Отримано сигнал: " << *csq_resp << "\n";
    }
}
