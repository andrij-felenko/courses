#include <string>
#include <vector>
#include <cstdint>
#include <optional>
#include <string_view>

namespace katran {

enum class ForwardingMode : uint32_t {
    DirectServerReturn = 0,
    GenericUdpEncapsulation = 1,
    IpInIp = 2
};

struct VipConfig {
    std::string vip_address;
    uint16_t port{443};
    uint8_t protocol{6}; // TCP
    ForwardingMode mode{ForwardingMode::GenericUdpEncapsulation};
    uint32_t ring_size{65537};
};

struct BackendConfig {
    std::string address;
    uint16_t port{443};
    uint32_t weight{1};
    bool enabled{true};
};

class KatranLb {
public:
    KatranLb() = default;
    ~KatranLb() = default;

    // Завантаження скомпільованого eBPF байткоду в драйвер мережевої карти
    bool attach_to_interface(std::string_view ifname);

    // Від'єднання BPF програми та очищення карт пам'яті
    bool detach_from_interface(std::string_view ifname);

    // Реєстрація нового віртуального сервісу (VIP)
    bool add_vip(const VipConfig& vip);

    // Видалення віртуального сервісу та звільнення пов'язаних таблиць
    bool remove_vip(const VipConfig& vip);

    // Додавання реального сервера до пулу зазначеного VIP
    bool add_backend_to_vip(const VipConfig& vip, const BackendConfig& backend);

    // Видалення сервера з пулу VIP
    bool remove_backend_from_vip(const VipConfig& vip, const BackendConfig& backend);

    // Зміна відносної ваги сервера на льоту
    bool modify_backend_weight(const VipConfig& vip, std::string_view backend_addr, uint32_t new_weight);

    // Примусова перебудова таблиці Maglev та оновлення BPF Array Map
    bool recalculate_maglev_ring(const VipConfig& vip);

    // Зчитування лічильників продуктивності з BPF Per-CPU Map
    [[nodiscard]] uint64_t get_total_packets_forwarded() const noexcept;
    [[nodiscard]] uint64_t get_lru_miss_count() const noexcept;
    [[nodiscard]] uint64_t get_lru_hit_count() const noexcept;
};

} // namespace katran
