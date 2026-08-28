// cpp
#include <cstdint>

struct alignas(64) IoUringSqe {
    std::uint8_t   opcode;      // IORING_OP_SEND_ZC
    std::uint8_t   flags;       // IOSQE_FIXED_FILE тощо
    std::uint16_t  ioprio;      // Прапорці відправки: IORING_RECVSEND_FIXED_BUF
    std::int32_t   fd;          // Мережевий файловий дескриптор (сокет)
    std::uint64_t  off;         // Зміщення у фіксованому буфері
    std::uint64_t  addr;        // Вказівник на буфер користувача або offset
    std::uint32_t  len;         // Довжина буфера в байтах
    std::uint32_t  msg_flags;   // Мережеві прапорці сокета (MSG_DONTWAIT)
    std::uint64_t  user_data;   // 64-бітний тег користувача
    std::uint16_t  buf_index;   // Індекс фіксованого буфера у реєстрі
    std::uint16_t  personality; // Контекст прав доступу
    std::uint32_t  file_index;  // Індекс фіксованого сокета
    std::uint64_t  addr3;       // Розширені прапорці сповіщення
};
