#include <cstdint>
#include <cstddef>

/* Двійковий заголовок та типізований конверт повідомлення vhost-user у C++ */
struct alignas(4) VhostUserHeader {
    uint32_t request{0};       // Код запиту або відповіді (опкод)
    uint32_t flags{0};         // Бітові прапорці версії, напрямку та підтвердження
    uint32_t size{0};          // Розмір корисного навантаження (payload) у байтах
};

struct VhostUserMsgRaw {
    VhostUserHeader header;
    uint8_t payload[1024];
};
