#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>
#include <expected>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <endian.h>

struct TzHeader {
    char magic[4];
    char version;
    char reserved[15];
    uint32_t ttisgmtcnt;
    uint32_t ttisstdcnt;
    uint32_t leapcnt;
    uint32_t timecnt;
    uint32_t typecnt;
    uint32_t charcnt;
};

struct LocalType {
    int32_t utoff{0};
    bool is_dst{false};
    uint8_t desig_idx{0};
};

struct ZoneData {
    std::vector<int64_t> transitions;
    std::vector<uint8_t> type_indices;
    std::vector<LocalType> types;
    std::string char_table;
    std::string posix_tz;

    [[nodiscard]] const LocalType* resolve(int64_t target_time) const noexcept {
        if (transitions.empty() || target_time < transitions.front()) {
            for (const auto& t : types) {
                if (!t.is_dst) return &t;
            }
            return types.empty() ? nullptr : &types.front();
        }

        auto it = std::upper_bound(transitions.begin(), transitions.end(), target_time);
        size_t index = std::distance(transitions.begin(), it) - 1;
        uint8_t type_idx = type_indices[index];
        if (type_idx < types.size()) {
            return &types[type_idx];
        }
        return nullptr;
    }

    [[nodiscard]] std::string_view abbreviation(const LocalType& type) const noexcept {
        if (type.desig_idx < char_table.size()) {
            return std::string_view(char_table.data() + type.desig_idx);
        }
        return "UNKNOWN";
    }
};

static std::expected<TzHeader, std::string> read_header(std::ifstream& stream) {
    TzHeader hdr{};
    if (!stream.read(reinterpret_cast<char*>(&hdr), sizeof(TzHeader))) {
        return std::unexpected("Неможливо прочитати заголовок tzhead");
    }
    if (std::memcmp(hdr.magic, "TZif", 4) != 0) {
        return std::unexpected("Некоректний магічний підпис файлу (не TZif)");
    }
    hdr.ttisgmtcnt = be32toh(hdr.ttisgmtcnt);
    hdr.ttisstdcnt = be32toh(hdr.ttisstdcnt);
    hdr.leapcnt    = be32toh(hdr.leapcnt);
    hdr.timecnt    = be32toh(hdr.timecnt);
    hdr.typecnt    = be32toh(hdr.typecnt);
    hdr.charcnt    = be32toh(hdr.charcnt);
    return hdr;
}

static std::expected<ZoneData, std::string> parse_tzfile(const std::string& path) {
    std::ifstream file(path, std::ios::binary);
    if (!file) {
        return std::unexpected("Не вдалося відкрити файл: " + path);
    }

    auto hdr1 = read_header(file);
    if (!hdr1) return std::unexpected(hdr1.error());

    TzHeader header = *hdr1;

    /* Пропуск 32-бітного блоку V1 при наявності 64-бітного V2/V3 */
    if (header.version == '2' || header.version == '3') {
        std::streamoff skip_v1 = static_cast<std::streamoff>(header.timecnt) * 4
                               + static_cast<std::streamoff>(header.timecnt) * 1
                               + static_cast<std::streamoff>(header.typecnt) * 6
                               + static_cast<std::streamoff>(header.charcnt)
                               + static_cast<std::streamoff>(header.leapcnt) * 8
                               + static_cast<std::streamoff>(header.ttisstdcnt)
                               + static_cast<std::streamoff>(header.ttisgmtcnt);

        file.seekg(skip_v1, std::ios::cur);
        auto hdr2 = read_header(file);
        if (!hdr2) return std::unexpected("Помилка зчитування другого 64-бітного заголовка");
        header = *hdr2;
    }

    ZoneData zone;
    zone.transitions.resize(header.timecnt);
    zone.type_indices.resize(header.timecnt);
    zone.types.resize(header.typecnt);
    zone.char_table.resize(header.charcnt);

    /* 1. Зчитування 64-бітних переходів */
    for (uint32_t i = 0; i < header.timecnt; ++i) {
        uint64_t raw_val{0};
        file.read(reinterpret_cast<char*>(&raw_val), sizeof(raw_val));
        zone.transitions[i] = static_cast<int64_t>(be64toh(raw_val));
    }

    /* 2. Зчитування індексів типів */
    if (header.timecnt > 0) {
        file.read(reinterpret_cast<char*>(zone.type_indices.data()), header.timecnt);
    }

    /* 3. Зчитування структур ttinfo */
    for (uint32_t i = 0; i < header.typecnt; ++i) {
        uint32_t raw_utoff{0};
        uint8_t isdst{0}, desigidx{0};
        file.read(reinterpret_cast<char*>(&raw_utoff), 4);
        file.read(reinterpret_cast<char*>(&isdst), 1);
        file.read(reinterpret_cast<char*>(&desigidx), 1);

        zone.types[i].utoff = static_cast<int32_t>(be32toh(raw_utoff));
        zone.types[i].is_dst = (isdst != 0);
        zone.types[i].desig_idx = desigidx;
    }

    /* 4. Зчитування таблиці абревіатур */
    if (header.charcnt > 0) {
        file.read(zone.char_table.data(), header.charcnt);
    }

    /* 5. Пропуск високосних секунд та прапорців */
    std::streamoff skip_tail = static_cast<std::streamoff>(header.leapcnt) * 12
                             + static_cast<std::streamoff>(header.ttisstdcnt)
                             + static_cast<std::streamoff>(header.ttisgmtcnt);
    file.seekg(skip_tail, std::ios::cur);

    /* 6. Хвостове правило POSIX TZ */
    if (file.get() == '\n') {
        std::getline(file, zone.posix_tz);
    }

    if (!file) {
        return std::unexpected("Помилка під час зчитування тіла бінарного tzfile");
    }

    return zone;
}

int main(int argc, char** argv) {
    const std::string path = (argc > 1) ? argv[1] : "/etc/localtime";
    const auto now_epoch = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());

    auto result = parse_tzfile(path);
    if (!result) {
        std::cerr << "Помилка розбору: " << result.error() << '\n';
        return 1;
    }

    const auto& zone = *result;
    const auto* active = zone.resolve(now_epoch);
    if (!active) {
        std::cerr << "Не вдалося визначити активне правило часу.\n";
        return 1;
    }

    int hours = active->utoff / 3600;
    int minutes = std::abs(active->utoff % 3600) / 60;

    std::cout << "Файл часового поясу : " << path << '\n';
    std::cout << "Кількість переходів : " << zone.transitions.size() << '\n';
    std::cout << "Поточна мітка time_t: " << now_epoch << " (UTC)\n";
    std::cout << "Активне зміщення    : " << (hours >= 0 ? "+" : "") << hours << ":"
              << (minutes < 10 ? "0" : "") << minutes << " (" << active->utoff << " с)\n";
    std::cout << "Режим літнього часу : " << (active->is_dst ? "ТАК (DST активний)" : "НІ (Стандартний час)") << '\n';
    std::cout << "Абревіатура зони    : " << zone.abbreviation(*active) << '\n';
    if (!zone.posix_tz.empty()) {
        std::cout << "Правило POSIX TZ    : " << zone.posix_tz << '\n';
    }

    return 0;
}
