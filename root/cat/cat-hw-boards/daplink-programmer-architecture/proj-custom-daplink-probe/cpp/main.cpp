#include "daplink_controller.hpp"
#include <iostream>
#include <iomanip>

int main() {
    std::cout << "=====================================================" << std::endl;
    std::cout << "  Демонстрація C++ контролера CMSIS-DAP / DAPLink   " << std::endl;
    std::cout << "=====================================================" << std::endl;

    DAPLinkController dap;

    /* 1. Ініціалізація підключення по шині SWD */
    if (!dap.connect(DAPPort::SWD)) {
        std::cerr << "Не вдалося ініціалізувати SWD порт." << std::endl;
        return 1;
    }

    /* 2. Налаштування тактової частоти 2 МГц */
    if (!dap.set_clock(2000000)) {
        std::cerr << "Не вдалося встановити частоту SWJ Clock." << std::endl;
        return 1;
    }

    /* 3. Зчитування ідентифікаційного коду ядра цілі (IDCODE) */
    auto idcode = dap.read_idcode();
    if (idcode.has_value()) {
        std::cout << "[УСПІХ] Зчитано IDCODE цільового МК: 0x"
                  << std::hex << std::uppercase << std::setfill('0') << std::setw(8)
                  << idcode.value() << std::dec << std::endl;
    } else {
        std::cerr << "[ПОМИЛКА] Не вдалося зчитати IDCODE." << std::endl;
    }

    /* 4. Виконання перезапуску цільового мікроконтролера */
    if (dap.reset_target()) {
        std::cout << "[УСПІХ] Цільовий мікроконтролер успішно перезапущено." << std::endl;
    } else {
        std::cerr << "[ПОМИЛКА] Збій виконання команди скидання." << std::endl;
    }

    /* 5. Завершення сесії зневадження */
    dap.disconnect();
    std::cout << "[DAPLink] Сесію успішно завершено." << std::endl;

    return 0;
}
