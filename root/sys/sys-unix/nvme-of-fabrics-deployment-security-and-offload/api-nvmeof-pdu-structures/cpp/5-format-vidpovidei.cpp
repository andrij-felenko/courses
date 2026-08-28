#include <cstdint>
#include <array>

struct nvmf_disc_rsp_page_entry {
    std::uint8_t  trtype;        // Тип транспорту: 1 = RDMA, 3 = TCP, 4 = FC
    std::uint8_t  adrfam;        // Родина адрес: 1 = IPv4, 2 = IPv6, 3 = IB, 4 = FC
    std::uint8_t  subtype;       // Тип підсистеми: 1 = Discovery, 2 = NVM Subsystem
    std::uint8_t  treq;          // Запити транспорту: Secure channel support
    std::uint16_t portid;        // Номер порту таргета
    std::uint16_t cntlid;        // Ідентифікатор контролера
    std::uint16_t asqsz;         // Максимальний розмір адміністративної черги SQ
    std::array<std::uint8_t, 22> resv10;
    std::array<char, 32>  trsvcid;// Рядок сервісного порту, наприклад "4420"
    std::array<std::uint8_t, 192> resv64;
    std::array<char, 256> subnqn; // NQN підсистеми зберігання
    std::array<char, 256> traddr; // Мережева адреса (наприклад "192.168.1.100")
    std::array<char, 256> tsas;   // Transport Specific Address Subsystem
};
