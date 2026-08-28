#include <netinet/in.h>
#include <span>

/* C++ типізоване представлення запиту фільтрації для IPv4/IPv6 */
struct GenericGroupSourceRequest {
    uint32_t         interface_index{0};
    sockaddr_storage group_storage{};
    sockaddr_storage source_storage{};

    [[nodiscard]] group_source_req to_c_struct() const noexcept {
        return group_source_req{interface_index, group_storage, source_storage};
    }
};
