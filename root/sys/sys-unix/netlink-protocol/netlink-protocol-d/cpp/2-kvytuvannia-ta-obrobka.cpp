#include <linux/netlink.h>
#include <system_error>
#include <iostream>

// Обробка структури помилки nlmsgerr у C++ із використанням std::error_code
void handle_netlink_error(const nlmsgerr& err) {
    if (err.error != 0) {
        std::error_code ec(-err.error, std::generic_category());
        std::cerr << "Netlink помилка: " << ec.message() << " (код " << err.error << ")\n";
    }
}
