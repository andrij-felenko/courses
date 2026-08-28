#include <linux/netlink.h>
#include <system_error>
#include <iostream>

// Обробка nlmsgerr у C++ за допомогою std::error_code
void process_ack(const nlmsgerr& err) {
    if (err.error == 0) {
        std::cout << "Запит успішно підтверджено ядром (ACK)\n";
    } else {
        std::error_code ec(-err.error, std::generic_category());
        std::cerr << "Помилка виконання запиту: " << ec.message() << "\n";
    }
}
