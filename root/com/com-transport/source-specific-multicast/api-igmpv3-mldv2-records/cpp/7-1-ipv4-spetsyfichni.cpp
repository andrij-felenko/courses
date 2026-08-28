#include <netinet/in.h>
#include <string_view>

/* Ідіоматична C++ обгортка над структурою фільтрації джерела */
struct SsmSourceMembership {
    in_addr group_address{};
    in_addr source_address{};
    in_addr interface_address{};

    [[nodiscard]] ip_mreq_source to_c_struct() const noexcept {
        return ip_mreq_source{group_address, source_address, interface_address};
    }
};
