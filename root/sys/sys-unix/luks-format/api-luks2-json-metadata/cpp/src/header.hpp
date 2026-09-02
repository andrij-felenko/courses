// Дисковий дескриптор LUKS2 і читання копії метаданих.
// Дескриптор носія тримає RAII-клас, помилки їдуть у std::expected,
// а буфер зони живе у std::vector<std::byte> замість malloc/free.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <filesystem>
#include <span>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace luks2 {

inline constexpr std::size_t kMagicSize       = 6;
inline constexpr std::size_t kLabelSize       = 48;
inline constexpr std::size_t kChecksumAlgSize = 32;
inline constexpr std::size_t kSaltSize        = 64;
inline constexpr std::size_t kUuidSize        = 44;
inline constexpr std::size_t kSubsystemSize   = 48;
inline constexpr std::size_t kPaddingSize     = 180;
inline constexpr std::size_t kChecksumSize    = 64;
inline constexpr std::size_t kHdrPadSize      = 3584;
inline constexpr std::size_t kHdrTotalSize    = 4096;
inline constexpr std::size_t kCsumOffset      = 448;

inline constexpr std::uint64_t kHdrSizeMin = 16384;
inline constexpr std::uint64_t kHdrSizeMax = 4194304;

inline constexpr std::string_view kMagicValid{"LUKS\xba\xbe", kMagicSize};
inline constexpr std::string_view kMagicWriting{"SKUL\xba\xbe", kMagicSize};

// Стандартні зсуви копії заголовка — ними шукають вторинну, коли первинну вбито.
inline constexpr std::array<std::uint64_t, 9> kHeaderOffsets{
    16384, 32768, 65536, 131072, 262144, 524288, 1048576, 2097152, 4194304};

#pragma pack(push, 1)
struct HeaderDisk {
    char          magic[kMagicSize];             // 0x0000
    std::uint16_t version;                       // 0x0006
    std::uint64_t hdr_size;                      // 0x0008
    std::uint64_t seqid;                         // 0x0010
    char          label[kLabelSize];             // 0x0018
    char          csum_alg[kChecksumAlgSize];    // 0x0048
    std::uint8_t  salt[kSaltSize];               // 0x0068
    char          uuid[kUuidSize];               // 0x00A8
    char          subsystem[kSubsystemSize];     // 0x00D4
    std::uint64_t hdr_offset;                    // 0x0104
    std::uint8_t  padding[kPaddingSize];         // 0x010C
    std::uint8_t  csum[kChecksumSize];           // 0x01C0
    std::uint8_t  pad_to_4k[kHdrPadSize];        // 0x0200
};
#pragma pack(pop)

static_assert(sizeof(HeaderDisk) == kHdrTotalSize,
              "дескриптор LUKS2 мусить займати рівно 4096 байтів");

enum class Error {
    io,
    magic,
    write_in_progress,   // сигнатура "SKUL": запис копії обірвано
    version,
    hdr_size,
    hdr_offset,          // копію зсунули відносно її власного поля
    checksum_alg,
    checksum,
    json_terminator,
    json_padding,
    json_syntax,
    json_schema,
};

std::string_view describe(Error error) noexcept;

// Володіє дескриптором носія: закривається сам, копіюватися не вміє.
class Device {
public:
    static std::expected<Device, Error> open(const std::filesystem::path& path);

    Device(const Device&) = delete;
    Device& operator=(const Device&) = delete;
    Device(Device&& other) noexcept : fd_{std::exchange(other.fd_, -1)} {}
    Device& operator=(Device&& other) noexcept;
    ~Device();

    // Дочитує рівно стільки, скільки просили, або віддає Error::io.
    std::expected<void, Error> read_at(std::span<std::byte> dst,
                                       std::uint64_t offset) const;

private:
    explicit Device(int fd) noexcept : fd_{fd} {}
    int fd_{-1};
};

// Прочитана й перевірена копія метаданих: сигнатура, версія, розмір,
// власний зсув, контрольна сума й межі текстової області.
class Header {
public:
    static std::expected<Header, Error> read(const Device& device,
                                             std::uint64_t offset);

    std::uint64_t at_offset() const noexcept { return at_offset_; }
    std::uint64_t hdr_size() const noexcept { return hdr_size_; }
    std::uint64_t seqid() const noexcept { return seqid_; }

    std::string_view label() const noexcept { return label_; }
    std::string_view uuid() const noexcept { return uuid_; }
    std::string_view subsystem() const noexcept { return subsystem_; }
    std::string_view csum_alg() const noexcept { return csum_alg_; }

    std::string_view json() const noexcept;
    std::size_t json_capacity() const noexcept {
        return static_cast<std::size_t>(hdr_size_) - kHdrTotalSize;
    }

private:
    Header() = default;

    std::vector<std::byte> area_;
    std::string label_;
    std::string uuid_;
    std::string subsystem_;
    std::string csum_alg_;
    std::uint64_t at_offset_{0};
    std::uint64_t hdr_size_{0};
    std::uint64_t seqid_{0};
    std::size_t json_len_{0};
};

}  // namespace luks2
