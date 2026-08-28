#include <cstdint>
#include <array>
#include <span>

inline constexpr size_t DHCP_CHADDR_LEN = 16;
inline constexpr size_t DHCP_SNAME_LEN = 64;
inline constexpr size_t DHCP_FILE_LEN = 128;
inline constexpr uint32_t DHCP_MAGIC_COOKIE = 0x63825363;

#pragma pack(push, 1)
/* Фіксований 236-байтний заголовок DHCP/BOOTP (RFC 2131) */
struct DhcpPacketHeader {
    uint8_t  op;                                // Код операції: 1=BOOTREQUEST, 2=BOOTREPLY
    uint8_t  htype;                             // Тип апаратної адреси (1 = Ethernet)
    uint8_t  hlen;                              // Довжина апаратної адреси (6 для Ethernet)
    uint8_t  hops;                              // Кількість ретрансляцій (Relay Hops)
    uint32_t xid;                               // Ідентифікатор транзакції (Transaction ID)
    uint16_t secs;                              // Секунди від початку спроби
    uint16_t flags;                             // Біт 15: Broadcast Flag, біти 0-14: MBZ
    uint32_t ciaddr;                            // Client IP (заповнено лише у BOUND/RENEW)
    uint32_t yiaddr;                            // «Your» IP Address (виділена сервером)
    uint32_t siaddr;                            // Next Server IP Address (TFTP/PXE)
    uint32_t giaddr;                            // Relay Agent IP Address (GIADDR)
    std::array<uint8_t, DHCP_CHADDR_LEN> chaddr;// Апаратна адреса клієнта (MAC)
    std::array<char, DHCP_SNAME_LEN>     sname; // Символьне ім'я сервера
    std::array<char, DHCP_FILE_LEN>      file;  // Ім'я завантажувального файлу
    uint32_t magic_cookie;                      // Магічне число 0x63825363 (Big-Endian)
};
#pragma pack(pop)
