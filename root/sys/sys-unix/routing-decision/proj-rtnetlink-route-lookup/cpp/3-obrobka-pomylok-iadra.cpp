// У C++ обробка помилок Netlink інтегрується зі std::error_code або std::system_error
namespace net {
    struct NlMsgErr {
        int error{0};          /* Від'ємний код помилки POSIX (наприклад -ESRCH) */
        ::nlmsghdr msg{};      /* Копія заголовка запиту, який викликав помилку */

        [[nodiscard]] std::error_code code() const noexcept {
            return std::error_code(-error, std::generic_category());
        }
    };
}
