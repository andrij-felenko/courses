#pragma once

// Формат офлайн-контейнера .upkg: константи, заголовок, помилки.
// Читається з носія байт-у-байт, тому всі структури пакованi й
// фіксованого розміру — вставка поля ламає підпис усіх випущених пакетів.
//
//   [0   .. 127]  заголовок метаданих
//   [128 .. 191]  Ed25519-підпис ключем випуску над цими 128 байтами
//   [192 .. ...]  таблиця хешів: chunk_count записів по 32 байти
//   далі          потік чанків по 4096 байтів
//   далі          сектор квитанції, вирівняний на 4096

#include <array>
#include <cstdint>
#include <expected>
#include <string_view>

namespace upkg {

inline constexpr std::uint32_t kMagic = 0x47504B55u;         // "UPKG"
inline constexpr std::uint32_t kReceiptMagic = 0x50435255u;  // "URCP"
inline constexpr std::uint16_t kFormatVersion = 1;

inline constexpr std::size_t kHeaderSize = 128;
inline constexpr std::size_t kSignatureSize = 64;
inline constexpr std::size_t kHashSize = 32;
inline constexpr std::size_t kPublicKeySize = 32;
inline constexpr std::uint32_t kChunkSize = 4096;

// Стеля образу 16 МБ: не ліміт заради ліміту, а гарантія, що добуток
// chunk_count * kChunkSize не переповнить 32-бітне зміщення.
inline constexpr std::uint32_t kMaxChunks = 4096;
inline constexpr std::uint8_t kBootRetries = 3;

using Hash = std::array<std::uint8_t, kHashSize>;
using Signature = std::array<std::uint8_t, kSignatureSize>;
using PublicKey = std::array<std::uint8_t, kPublicKeySize>;

enum class Error : std::uint8_t {
    Io = 1,
    InvalidMagic,
    Format,
    HardwareMismatch,
    RollbackDetected,
    SignatureInvalid,
    TableHashMismatch,
    ChunkHashMismatch,
    FinalHashMismatch,
    FlashErase,
    FlashWrite,
    Crypto,
    NvsWrite
};

constexpr std::string_view describe(Error e) noexcept {
    switch (e) {
    case Error::Io:                return "носій недоступний";
    case Error::InvalidMagic:      return "це не пакет UPKG";
    case Error::Format:            return "поля заголовка суперечливі";
    case Error::HardwareMismatch:  return "образ для іншої плати";
    case Error::RollbackDetected:  return "спроба відкату версії";
    case Error::SignatureInvalid:  return "підпис випуску недійсний";
    case Error::TableHashMismatch: return "таблиця хешів підмінена";
    case Error::ChunkHashMismatch: return "чанк не збігся з таблицею";
    case Error::FinalHashMismatch: return "підсумковий хеш образу інший";
    case Error::FlashErase:        return "стирання Slot B не вдалося";
    case Error::FlashWrite:        return "запис у Slot B не вдався";
    case Error::Crypto:            return "криптоблок відмовив";
    case Error::NvsWrite:          return "стан завантаження не збережено";
    }
    return "невідомий код";
}

template <class T>
using Result = std::expected<T, Error>;

struct [[gnu::packed]] Header {
    std::uint32_t magic;
    std::uint16_t format_version;
    std::uint16_t target_hw_id;      // звіряється з OTP/eFuse плати
    std::uint32_t version_monotonic;
    std::uint32_t payload_size;
    std::uint32_t chunk_count;
    std::uint32_t chunk_size;
    Hash final_sha256;               // хеш усього образу
    Hash table_sha256;               // хеш таблиці хешів чанків
    std::array<std::uint8_t, 36> reserved;
};
static_assert(sizeof(Header) == kHeaderSize,
              "заголовок мусить лишатися рівно 128 байтів");

struct Policy {
    std::uint16_t hardware_id;       // код моделі з OTP
    std::uint32_t min_version;       // поріг із монотонних запобіжників
    std::uint32_t device_serial;
    PublicKey root_public_key;       // з eFuse/Boot ROM
};

enum class SlotFlag : std::uint8_t {
    Empty = 0x00,
    PendingVerify = 0xA5,
    Confirmed = 0x5A
};

struct [[gnu::packed]] BootState {
    std::uint32_t staged_version;
    SlotFlag flag;
    std::uint8_t boot_retries;
};

// Квитанція аудиту: технік везе її назад у сервіс як доказ того, що саме
// сталося на цьому пристрої. Підписана ключем самого пристрою.
struct [[gnu::packed]] ReceiptBody {
    std::uint32_t magic;
    std::uint32_t device_serial;
    std::uint16_t hw_id;
    std::uint16_t status;            // 0 == успіх, інакше код Error
    std::uint32_t version;
    Hash image_sha256;
    std::uint8_t boot_retries;
    std::array<std::uint8_t, 3> reserved;
};

struct [[gnu::packed]] Receipt {
    ReceiptBody body;
    Signature signature;
};

constexpr std::uint32_t tableOffset() noexcept {
    return static_cast<std::uint32_t>(kHeaderSize + kSignatureSize);
}

constexpr std::uint32_t tableBytes(const Header& h) noexcept {
    return h.chunk_count * static_cast<std::uint32_t>(kHashSize);
}

constexpr std::uint32_t payloadOffset(const Header& h) noexcept {
    return tableOffset() + tableBytes(h);
}

constexpr std::uint32_t chunkLength(const Header& h, std::uint32_t idx) noexcept {
    const std::uint32_t left = h.payload_size - idx * kChunkSize;
    return left < kChunkSize ? left : kChunkSize;
}

// Квитанція лягає в окремий сектор одразу за навантаженням.
constexpr std::uint32_t receiptOffset(const Header& h) noexcept {
    const std::uint32_t end = payloadOffset(h) + h.payload_size;
    return (end + kChunkSize - 1) / kChunkSize * kChunkSize;
}

}  // namespace upkg
