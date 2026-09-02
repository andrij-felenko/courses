#include "header.hpp"

#include <fcntl.h>
#include <unistd.h>

#include <openssl/evp.h>

#include <algorithm>
#include <bit>
#include <cerrno>
#include <cstring>
#include <memory>
#include <ranges>

namespace luks2 {
namespace {

struct MdCtxDeleter {
    void operator()(EVP_MD_CTX* ctx) const noexcept { EVP_MD_CTX_free(ctx); }
};
using MdCtx = std::unique_ptr<EVP_MD_CTX, MdCtxDeleter>;

template <typename T>
T from_big_endian(T value) noexcept {
    if constexpr (std::endian::native == std::endian::little) {
        return std::byteswap(value);
    } else {
        return value;
    }
}

// Поля-рядки на диску не зобов'язані мати нульовий байт — ріжемо самі.
std::string field_string(std::span<const char> field) {
    const auto* end = static_cast<const char*>(
        std::memchr(field.data(), '\0', field.size()));
    const auto len = end ? static_cast<std::size_t>(end - field.data()) : field.size();
    return std::string{field.data(), len};
}

// Сума рахується над усім блоком із зануленим полем csum. Замість копії буфера
// подаємо дайджесту три шматки: до поля, шістдесят чотири нулі, після поля.
std::expected<void, Error> verify_checksum(std::span<const std::byte> area,
                                           std::string_view algorithm) {
    const std::string name{algorithm};
    const EVP_MD* md = EVP_get_digestbyname(name.c_str());
    if (md == nullptr) {
        return std::unexpected(Error::checksum_alg);  // напр. "crc32" — його в EVP немає
    }
    const int md_len = EVP_MD_size(md);
    if (md_len <= 0 || static_cast<std::size_t>(md_len) > kChecksumSize) {
        return std::unexpected(Error::checksum_alg);
    }

    MdCtx ctx{EVP_MD_CTX_new()};
    if (!ctx) {
        return std::unexpected(Error::checksum);
    }

    static constexpr std::array<std::byte, kChecksumSize> zeros{};
    const auto tail = area.subspan(kCsumOffset + kChecksumSize);

    if (EVP_DigestInit_ex(ctx.get(), md, nullptr) != 1 ||
        EVP_DigestUpdate(ctx.get(), area.data(), kCsumOffset) != 1 ||
        EVP_DigestUpdate(ctx.get(), zeros.data(), zeros.size()) != 1 ||
        EVP_DigestUpdate(ctx.get(), tail.data(), tail.size()) != 1) {
        return std::unexpected(Error::checksum);
    }

    std::array<unsigned char, EVP_MAX_MD_SIZE> calculated{};
    unsigned int calculated_len = 0;
    if (EVP_DigestFinal_ex(ctx.get(), calculated.data(), &calculated_len) != 1 ||
        calculated_len != static_cast<unsigned int>(md_len)) {
        return std::unexpected(Error::checksum);
    }

    const auto stored = area.subspan(kCsumOffset, calculated_len);
    if (std::memcmp(stored.data(), calculated.data(), calculated_len) != 0) {
        return std::unexpected(Error::checksum);
    }
    return {};
}

}  // namespace

std::string_view describe(Error error) noexcept {
    switch (error) {
    case Error::io:                return "помилка читання носія";
    case Error::magic:             return "немає сигнатури LUKS2";
    case Error::write_in_progress: return "сигнатура SKUL — запис копії було обірвано";
    case Error::version:           return "версія формату не 2";
    case Error::hdr_size:          return "неприпустимий hdr_size";
    case Error::hdr_offset:        return "hdr_offset не збігається з фактичним зсувом";
    case Error::checksum_alg:      return "невідомий алгоритм контрольної суми";
    case Error::checksum:          return "контрольна сума не збіглася";
    case Error::json_terminator:   return "область JSON не має нульового термінатора";
    case Error::json_padding:      return "хвіст після документа JSON не занулено";
    case Error::json_syntax:       return "документ JSON синтаксично поламаний";
    case Error::json_schema:       return "у корені немає обов'язкових словників";
    }
    return "невідома помилка";
}

std::expected<Device, Error> Device::open(const std::filesystem::path& path) {
    const int fd = ::open(path.c_str(), O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        return std::unexpected(Error::io);
    }
    return Device{fd};
}

Device& Device::operator=(Device&& other) noexcept {
    if (this != &other) {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = std::exchange(other.fd_, -1);
    }
    return *this;
}

Device::~Device() {
    if (fd_ >= 0) {
        ::close(fd_);
    }
}

std::expected<void, Error> Device::read_at(std::span<std::byte> dst,
                                           std::uint64_t offset) const {
    while (!dst.empty()) {
        const ssize_t got = ::pread(fd_, dst.data(), dst.size(),
                                    static_cast<off_t>(offset));
        if (got < 0) {
            if (errno == EINTR) {
                continue;
            }
            return std::unexpected(Error::io);
        }
        if (got == 0) {
            return std::unexpected(Error::io);  // пристрій коротший за hdr_size
        }
        dst = dst.subspan(static_cast<std::size_t>(got));
        offset += static_cast<std::uint64_t>(got);
    }
    return {};
}

std::string_view Header::json() const noexcept {
    return std::string_view{
        reinterpret_cast<const char*>(area_.data()) + kHdrTotalSize, json_len_};
}

std::expected<Header, Error> Header::read(const Device& device,
                                          std::uint64_t offset) {
    HeaderDisk disk{};
    std::array<std::byte, kHdrTotalSize> descriptor{};
    if (auto ok = device.read_at(descriptor, offset); !ok) {
        return std::unexpected(ok.error());
    }
    std::memcpy(&disk, descriptor.data(), sizeof(disk));

    // 1. Сигнатура: "SKUL" — не сміття, а перервана транзакція запису.
    const std::string_view magic{disk.magic, kMagicSize};
    if (magic == kMagicWriting) {
        return std::unexpected(Error::write_in_progress);
    }
    if (magic != kMagicValid) {
        return std::unexpected(Error::magic);
    }

    // 2. Версія.
    if (from_big_endian(disk.version) != 2) {
        return std::unexpected(Error::version);
    }

    // 3. Розмір зони: степінь двійки в межах 16 КіБ … 4 МіБ.
    const std::uint64_t hdr_size = from_big_endian(disk.hdr_size);
    if (hdr_size < kHdrSizeMin || hdr_size > kHdrSizeMax ||
        !std::has_single_bit(hdr_size)) {
        return std::unexpected(Error::hdr_size);
    }

    // 4. Копія знає власний зсув — так ловлять образ, покладений не туди.
    if (from_big_endian(disk.hdr_offset) != offset) {
        return std::unexpected(Error::hdr_offset);
    }

    Header header;
    header.area_.resize(static_cast<std::size_t>(hdr_size));
    if (auto ok = device.read_at(header.area_, offset); !ok) {
        return std::unexpected(ok.error());
    }

    // 5. Контрольна сума всього блоку.
    header.csum_alg_ = field_string({disk.csum_alg, kChecksumAlgSize});
    if (auto ok = verify_checksum(header.area_, header.csum_alg_); !ok) {
        return std::unexpected(ok.error());
    }

    // 6. Межі текстової області: термінатор і занулений хвіст.
    const auto text = std::span<const std::byte>{header.area_}.subspan(kHdrTotalSize);
    const auto nul = std::ranges::find(text, std::byte{0});
    if (nul == text.end()) {
        return std::unexpected(Error::json_terminator);
    }
    header.json_len_ = static_cast<std::size_t>(std::ranges::distance(text.begin(), nul));
    const auto padding = text.subspan(header.json_len_);
    if (!std::ranges::all_of(padding, [](std::byte b) { return b == std::byte{0}; })) {
        return std::unexpected(Error::json_padding);
    }

    header.label_ = field_string({disk.label, kLabelSize});
    header.uuid_ = field_string({disk.uuid, kUuidSize});
    header.subsystem_ = field_string({disk.subsystem, kSubsystemSize});
    header.at_offset_ = offset;
    header.hdr_size_ = hdr_size;
    header.seqid_ = from_big_endian(disk.seqid);
    return header;
}

}  // namespace luks2
