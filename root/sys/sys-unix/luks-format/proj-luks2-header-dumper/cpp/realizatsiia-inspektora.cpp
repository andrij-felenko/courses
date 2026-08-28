#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <expected>
#include <cstdint>
#include <cstring>
#include <endian.h>

namespace luks {

constexpr std::string_view MAGIC_SIGNATURE = "LUKS\xba\xbe";
constexpr std::size_t HDR_SIZE = 4096;
constexpr std::size_t DEFAULT_HDR_SIZE = 4 * 1024 * 1024;

struct alignas(1) HeaderDisk {
    char     magic[6];
    uint16_t version;
    uint64_t hdr_size;
    uint64_t seqid;
    char     label[48];
    char     csum_alg[32];
    uint8_t  salt[64];
    char     uuid[44];
    char     subsystem[48];
    uint64_t hdr_offset;
    uint8_t  padding[184];
    uint8_t  csum[64];
    uint8_t  pad_to_4k[3584];
};
static_assert(sizeof(HeaderDisk) == HDR_SIZE, "Розмір HeaderDisk мусить бути рівно 4096 байтів");

struct HeaderInfo {
    uint16_t version;
    uint64_t hdr_size;
    uint64_t seqid;
    std::string label;
    std::string subsystem;
    std::string uuid;
    std::string csum_alg;
    uint64_t hdr_offset;
};

class Inspector {
public:
    explicit Inspector(std::string_view path) : file_(std::string(path), std::ios::binary) {}

    [[nodiscard]] bool isOpen() const noexcept { return file_.is_open(); }

    std::expected<HeaderInfo, std::string> readHeaderAt(std::streamoff offset, std::string_view label) {
        if (!file_.seekg(offset, std::ios::beg)) {
            return std::unexpected("Помилка позиціонування файлового покажчика");
        }

        HeaderDisk raw{};
        if (!file_.read(reinterpret_cast<char*>(&raw), sizeof(raw))) {
            return std::unexpected(std::string("[") + std::string(label) + "] Помилка читання 4096 байтів");
        }

        if (std::string_view(raw.magic, 6) != MAGIC_SIGNATURE) {
            return std::unexpected(std::string("[") + std::string(label) + "] Сигнатура magic не відповідає LUKS2");
        }

        HeaderInfo info{
            .version = be16toh(raw.version),
            .hdr_size = be64toh(raw.hdr_size),
            .seqid = be64toh(raw.seqid),
            .label = std::string(raw.label, strnlen(raw.label, sizeof(raw.label))),
            .subsystem = std::string(raw.subsystem, strnlen(raw.subsystem, sizeof(raw.subsystem))),
            .uuid = std::string(raw.uuid, strnlen(raw.uuid, sizeof(raw.uuid))),
            .csum_alg = std::string(raw.csum_alg, strnlen(raw.csum_alg, sizeof(raw.csum_alg))),
            .hdr_offset = be64toh(raw.hdr_offset)
        };

        return info;
    }

private:
    std::ifstream file_;
};

} // namespace luks

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <пристрій_або_файл_образу>\n";
        return 1;
    }

    luks::Inspector inspector(argv[1]);
    if (!inspector.isOpen()) {
        std::cerr << "Не вдалося відкрити вказаний файл або пристрій: " << argv[1] << '\n';
        return 1;
    }

    auto primary = inspector.readHeaderAt(0, "Первинний заголовок");
    std::uint64_t secondaryOffset = luks::DEFAULT_HDR_SIZE;
    if (primary) {
        secondaryOffset = primary->hdr_size;
    }

    auto secondary = inspector.readHeaderAt(static_cast<std::streamoff>(secondaryOffset), "Вторинний заголовок");

    if (!primary && !secondary) {
        std::cerr << "Критична помилка: на носії відсутні дійсні заголовки LUKS2.\n";
        return 1;
    }

    auto printInfo = [](const luks::HeaderInfo& info, std::string_view title) {
        std::cout << "=== " << title << " (Зсув: 0x" << std::hex << info.hdr_offset << std::dec << ") ===\n"
                  << "  Версія формату:      " << info.version << '\n'
                  << "  Розмір метаданих:    " << info.hdr_size << " байтів (" << (info.hdr_size / (1024 * 1024)) << " МіБ)\n"
                  << "  Номер транзакції:    " << info.seqid << " (seqid)\n"
                  << "  Мітка (Label):       " << (info.label.empty() ? "<пусто>" : info.label) << '\n'
                  << "  UUID тому:           " << info.uuid << '\n'
                  << "  Алгоритм суми:       " << info.csum_alg << '\n';
    };

    if (primary) printInfo(*primary, "Первинний заголовок");
    if (secondary) printInfo(*secondary, "Вторинний заголовок");

    std::cout << "\n--- Арбітраж стану заголовків ---\n";
    if (primary && secondary) {
        if (primary->seqid >= secondary->seqid) {
            std::cout << "Активним є ПЕРВИННИЙ заголовок (seqid = " << primary->seqid << " >= " << secondary->seqid << ")\n";
        } else {
            std::cout << "Активним є ВТОРИННИЙ заголовок (seqid = " << secondary->seqid << " > " << primary->seqid << ")\n";
        }
    } else if (primary) {
        std::cout << "Вторинний заголовок пошкоджено. Активним є ПЕРВИННИЙ (seqid = " << primary->seqid << ")\n";
    } else {
        std::cout << "Первинний заголовок пошкоджено. Активним є ВТОРИННИЙ (seqid = " << secondary->seqid << ")\n";
    }

    return 0;
}
