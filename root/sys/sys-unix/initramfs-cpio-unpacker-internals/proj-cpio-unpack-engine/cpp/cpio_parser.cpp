// cpio_parser.cpp — Ідіоматичний парсер cpio newc мовою C++20
#include <iostream>
#include <span >
#include <string_view>
#include <system_error>
#include <expected>
#include <filesystem>
#include <fstream>
#include <charconv>
#include <cstring>
#include <unordered_map>

namespace fs = std::filesystem;

namespace cpio {

constexpr std::string_view MAGIC_NEWC = "070701";
constexpr std::string_view MAGIC_CRC  = "070702";
constexpr std::string_view TRAILER     = "TRAILER!!!";

struct [[gnu::packed]] Header {
    char magic[6];
    char ino[8];
    char mode[8];
    char uid[8];
    char gid[8];
    char nlink[8];
    char mtime[8];
    char filesize[8];
    char maj[8];
    char min[8];
    char rmaj[8];
    char rmin[8];
    char namesize[8];
    char chksum[8];
};

enum class ParseError {
    InvalidMagic,
    OutOfBounds,
    MissingNullTerminator,
    PathTraversalAttempt,
    ExtractionFailed
};

/* Безпечна C++20 конверсія 8-значного hex ASCII в uint32_t через std::from_chars */
constexpr std::optional<uint32_t> parse_hex8(std::string_view sv) noexcept {
    if (sv.size() < 8) return std::nullopt;
    uint32_t val = 0;
    auto [ptr, ec] = std::from_chars(sv.data(), sv.data() + 8, val, 16);
    if (ec == std::errc{}) return val;
    return std::nullopt;
}

constexpr size_t align4(size_t offset) noexcept {
    return (4 - (offset % 4)) % 4;
}

class Unpacker {
public:
    static std::expected<size_t, ParseError> unpack(
        std::span<const std::byte> buffer, 
        const fs::path& target_dir) 
    {
        size_t offset = 0;
        std::unordered_map<uint32_t, fs::path> hardlinks;

        while (offset + sizeof(Header) <= buffer.size()) {
            const auto* hdr = reinterpret_cast<const Header*>(buffer.data() + offset);
            std::string_view magic{hdr->magic, 6};

            if (magic != MAGIC_NEWC && magic != MAGIC_CRC) {
                return std::unexpected(ParseError::InvalidMagic);
            }

            auto ino      = parse_hex8({hdr->ino, 8});
            auto mode     = parse_hex8({hdr->mode, 8});
            auto filesize = parse_hex8({hdr->filesize, 8});
            auto namesize = parse_hex8({hdr->namesize, 8});

            if (!ino || !mode || !filesize || !namesize) {
                return std::unexpected(ParseError::InvalidMagic);
            }

            offset += sizeof(Header);

            if (offset + *namesize > buffer.size()) {
                return std::unexpected(ParseError::OutOfBounds);
            }

            std::string_view name{
                reinterpret_cast<const char*>(buffer.data() + offset), 
                *namesize > 0 ? *namesize - 1 : 0
            };

            if (name == TRAILER) {
                return offset; // Успішно досягнуто маркер кінця
            }

            if (name.find("../") != std::string_view::npos) {
                return std::unexpected(ParseError::PathTraversalAttempt);
            }

            offset += *namesize;
            offset += align4(sizeof(Header) + *namesize);

            if (offset + *filesize > buffer.size()) {
                return std::unexpected(ParseError::OutOfBounds);
            }

            std::span<const std::byte> payload = buffer.subspan(offset, *filesize);

            if (name != "." && !name.empty()) {
                fs::path out_path = target_dir / name;
                if (!extract_node(out_path, *ino, *mode, payload, hardlinks)) {
                    return std::unexpected(ParseError::ExtractionFailed);
                }
            }

            offset += *filesize;
            offset += align4(*filesize);
        }

        return offset;
    }

private:
    static bool extract_node(
        const fs::path& path, 
        uint32_t ino,
        uint32_t mode, 
        std::span<const std::byte> payload,
        std::unordered_map<uint32_t, fs::path>& hardlinks) 
    {
        std::error_code ec;
        uint32_t type = mode & 0170000;

        // Перевірка наявних жорстких посилань
        if (type == 0100000 && payload.empty()) {
            if (auto it = hardlinks.find(ino); it != hardlinks.end()) {
                fs::create_hard_link(it->second, path, ec);
                return !ec;
            }
        }

        if (type == 0040000) { // S_IFDIR
            fs::create_directories(path, ec);
        } else if (type == 0100000) { // S_IFREG
            if (path.has_parent_path()) {
                fs::create_directories(path.parent_path(), ec);
            }
            std::ofstream file(path, std::ios::binary);
            if (!file) return false;
            file.write(reinterpret_cast<const char*>(payload.data()), payload.size());
            fs::permissions(path, static_cast<fs::perms>(mode & 0777), ec);
            hardlinks[ino] = path;
        } else if (type == 0120000) { // S_IFLNK
            std::string_view target{
                reinterpret_cast<const char*>(payload.data()), 
                payload.size()
            };
            fs::create_symlink(target, path, ec);
        }
        return !ec;
    }
};

} // namespace cpio
