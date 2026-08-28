#include <fcntl.h>
#include <unistd.h>
#include <string_view>
#include <system_error>

namespace legacy_service {

/* Код привілейованого заступника (виконується з UID 0) */
void handle_client_request(std::string_view user_chosen_path, std::string_view data) {
    /* 1. Запис результатів клієнта */
    int fd_out = ::open(user_chosen_path.data(), O_WRONLY | O_CREAT | O_TRUNC, 0600);
    if (fd_out >= 0) {
        ::write(fd_out, data.data(), data.size());
        ::close(fd_out);
    }

    /* 2. Запис внутрішнього системного білінгу від власного імені */
    int fd_bill = ::open("/var/log/service.bill", O_WRONLY | O_APPEND);
    if (fd_bill >= 0) {
        constexpr std::string_view record = "BILLING_RECORD: +1 operation\n";
        ::write(fd_bill, record.data(), record.size());
        ::close(fd_bill);
    }
}

} // namespace legacy_service
