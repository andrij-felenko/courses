# ⚙️ Розбір бінарного формату tzfile(5)

Файли часових поясів у каталозі `/usr/share/zoneinfo/` та символічне посилання `/etc/localtime` не є текстовими таблицями — це скомпільовані бінарні файли стандарту RFC 8536 (`tzfile(5)`). Коли системна бібліотека або прикладний сервіс викликає `localtime_r()`, вона не виконує зовнішніх команд і не звертається до демонів, а безпосередньо відкриває відповідний бінарний файл, відображає його в пам'ять за допомогою системного виклику `mmap(2)` і здійснює двійковий пошук за масивом часових переходів.

Розбір структури `tzfile` демонструє, як саме абстрактні політичні правила переведення годинників перетворюються на компактні бінарні таблиці зміщень, індексів та абревіатур, придатні для швидкого пошуку за `O(log N)`.

## Задача та специфікація формату

Необхідно реалізувати низькорівневий парсер, який приймає шлях до бінарного файлу зони (наприклад, `/usr/share/zoneinfo/Europe/Kyiv` або системне посилання `/etc/localtime`) та довільну часову позначку `time_t`, зчитує 64-бітний блок заголовка й таблиць, знаходить активне на цю мить зміщення від UTC, прапорець літнього часу (DST), абревіатуру поясу (наприклад, `EET` або `EEST`) та завершальне правило POSIX TZ.

Текстові файли бази даних IANA (`tzdata`), що містять описи правил `Rule` та зон `Zone`, компілюються утилітою `zic` (Zone Information Compiler) у бінарний вигляд. Згідно зі специфікацією RFC 8536, сучасний файл `tzfile` версії 2 або 3 містить два послідовні блоки даних:

1. **Застарілий 32-бітний блок v1** — розташований на самому початку файлу після першого 44-байтного заголовка `struct tzhead`. Він призначений для сумісності зі старими 32-бітними програмами. У ньому часові позначки переходів займають рівно 4 байти і не можуть описувати події після 19 січня 2038 року.
2. **Повнорозмірний 64-бітний блок v2/v3** — починається одразу за завершенням першого блоку. Він відкривається власним 44-байтним заголовком `struct tzhead` і містить 8-байтні знакові цілі для всіх моментів переходу, що повністю усуває обмеження 2038 року і дозволяє адресувати як далеке минуле, так і майбутнє на сотні мільярдів років.
3. **Хвостовий рядок POSIX TZ** — розташований наприкінці файлу в обрамленні символів нового рядка `\n...\n`. Він задає алгоритмічну формулу для обчислення майбутніх переходів за межами останнього явного запису в таблиці.

Структура 44-байтного заголовка (`struct tzhead`):

```
+---------------+---------+----------------------------------------------+
| Поле          | Розмір  | Опис                                         |
+---------------+---------+----------------------------------------------+
| tzh_magic     | 4 байти | Магічні байти "TZif"                         |
| tzh_version   | 1 байт  | Версія: '\0' (v1), '2' (v2), '3' (v3)        |
| tzh_reserved  | 15 байт | Зарезервовано для майбутніх розширень (нулі) |
| tzh_ttisgmtcnt| 4 байти | Кількість прапорців UTC/локальний час        |
| tzh_ttisstdcnt| 4 байти | Кількість прапорців стандартний/настінний час|
| tzh_leapcnt   | 4 байти | Кількість записів високосних секунд          |
| tzh_timecnt   | 4 байти | Кількість моментів переходу часу             |
| tzh_typecnt   | 4 байти | Кількість структур опису типу (ttinfo)       |
| tzh_charcnt   | 4 байти | Довжина рядка назв часових поясів (символи)  |
+---------------+---------+----------------------------------------------+
```

Усі цілочислові поля заголовка та масивів зберігаються у мережевому порядку байтів (**big-endian**, від старшого до молодшого), тому на архітектурах x86-64 та ARM їх обов'язково треба конвертувати у порядок байтів хоста за допомогою функцій `be32toh()` та `be64toh()`.

## Організація даних у тілі файлу

Після заголовка 64-бітного блоку дані розташовані суворо одне за одним без вирівнювання:
* `timecnt` 8-байтних цілих чисел (`int64_t`) — упорядкований за зростанням масив часових позначок `time_t` за шкалою UTC, коли в юрисдикції відбувалася зміна зміщення або перехід на літній/зимовий час;
* `timecnt` однобайтних беззнакових індексів (`uint8_t`) — кожен байт пов'язує відповідний перехід із порядковим номером структури `ttinfo`;
* `typecnt` 6-байтних записів `struct ttinfo` — опис характеристик локального часу:
  - 4 байти `tt_utoff` (`int32_t`) — знакове зміщення від UTC у секундах (наприклад, `+7200` для EET або `-18000` для EST);
  - 1 байт `tt_isdst` (`uint8_t`) — прапорець літнього часу (`0` для стандартного/зимового, `1` для DST);
  - 1 байт `tt_desigidx` (`uint8_t`) — зсув початку нуль-термінованого рядка назви (наприклад, `"EET"` чи `"EEST"`) у таблиці символів;
* `charcnt` байтів таблиці символів — конкатенація назв зон, розділених нульовими байтами (`\0`);
* `leapcnt * 12` байтів таблиці високосних секунд — пари `(8 байтів time_t, 4 байти ціле)`, що вказують, коли саме була вставлена високосна секунда і яка сумарна поправка діє після неї (застосовується виключно у файлах каталогу `right/`);
* `ttisstdcnt` та `ttisgmtcnt` байтів службових прапорців компілятора `zic`.

Алгоритм пошуку зміщення для заданого моменту `T` є двійковим пошуком: у масиві переходів знаходиться найбільший елемент, що не перевищує `T`. Його індекс вказує на дескриптор `ttinfo`, звідки безпосередньо зчитуються зміщення в секундах та текстова назва зони.

## Реалізація парсера

Код зчитує перший заголовок, обчислює розмір 32-бітного блоку даних, переходить до другого заголовка версії 2/3, зчитує 64-бітні переходи та структури `ttinfo`, а потім виконує пошук актуального зміщення для заданого моменту часу.

:::tabs
```c
#define _DEFAULT_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <endian.h>
#include <time.h>
#include <errno.h>

struct tz_header {
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

struct ttinfo {
    int32_t utoff;      /* Зміщення від UTC у секундах */
    uint8_t isdst;      /* 0 — зимовий / стандартний, 1 — літній DST */
    uint8_t desigidx;   /* Зсув назви абревіатури в таблиці символів */
};

struct parsed_tz {
    uint32_t timecnt;
    uint32_t typecnt;
    int64_t *transitions;
    uint8_t *type_indices;
    struct ttinfo *types;
    char *char_table;
    char posix_tz[128];
};

static int read_header(FILE *f, struct tz_header *hdr) {
    if (fread(hdr, sizeof(struct tz_header), 1, f) != 1) {
        return -1;
    }
    if (memcmp(hdr->magic, "TZif", 4) != 0) {
        return -2;
    }
    hdr->ttisgmtcnt = be32toh(hdr->ttisgmtcnt);
    hdr->ttisstdcnt = be32toh(hdr->ttisstdcnt);
    hdr->leapcnt    = be32toh(hdr->leapcnt);
    hdr->timecnt    = be32toh(hdr->timecnt);
    hdr->typecnt    = be32toh(hdr->typecnt);
    hdr->charcnt    = be32toh(hdr->charcnt);
    return 0;
}

static void free_tz(struct parsed_tz *tz) {
    if (!tz) return;
    free(tz->transitions);
    free(tz->type_indices);
    free(tz->types);
    free(tz->char_table);
    memset(tz, 0, sizeof(*tz));
}

static int parse_tzfile64(const char *path, struct parsed_tz *tz) {
    memset(tz, 0, sizeof(*tz));
    FILE *f = fopen(path, "rb");
    if (!f) return -1;

    struct tz_header h1;
    if (read_header(f, &h1) != 0) {
        fclose(f);
        return -2;
    }

    /* Якщо файл версії 2 або 3, пропускаємо старий 32-бітний блок */
    if (h1.version == '2' || h1.version == '3') {
        long skip_v1 = (long)h1.timecnt * 4       /* transitions (32-bit) */
                     + (long)h1.timecnt * 1       /* type indices */
                     + (long)h1.typecnt * 6       /* ttinfo records (4+1+1) */
                     + (long)h1.charcnt           /* designations */
                     + (long)h1.leapcnt * 8       /* leap records (4+4) */
                     + (long)h1.ttisstdcnt * 1    /* standard/wall flags */
                     + (long)h1.ttisgmtcnt * 1;   /* ut/local flags */

        if (fseek(f, skip_v1, SEEK_CUR) != 0) {
            fclose(f);
            return -3;
        }

        struct tz_header h2;
        if (read_header(f, &h2) != 0) {
            fclose(f);
            return -4;
        }
        h1 = h2;
    }

    tz->timecnt = h1.timecnt;
    tz->typecnt = h1.typecnt;

    /* Виділення пам'яті під таблиці 64-бітного блоку */
    tz->transitions = malloc(sizeof(int64_t) * (h1.timecnt > 0 ? h1.timecnt : 1));
    tz->type_indices = malloc(sizeof(uint8_t) * (h1.timecnt > 0 ? h1.timecnt : 1));
    tz->types = malloc(sizeof(struct ttinfo) * (h1.typecnt > 0 ? h1.typecnt : 1));
    tz->char_table = malloc(h1.charcnt > 0 ? h1.charcnt : 1);

    if (!tz->transitions || !tz->type_indices || !tz->types || !tz->char_table) {
        free_tz(tz);
        fclose(f);
        return -5;
    }

    /* 1. Зчитування 64-бітних часових переходів */
    for (uint32_t i = 0; i < h1.timecnt; ++i) {
        int64_t raw_val;
        if (fread(&raw_val, sizeof(int64_t), 1, f) != 1) {
            free_tz(tz); fclose(f); return -6;
        }
        tz->transitions[i] = (int64_t)be64toh((uint64_t)raw_val);
    }

    /* 2. Зчитування індексів типів */
    if (h1.timecnt > 0 && fread(tz->type_indices, 1, h1.timecnt, f) != h1.timecnt) {
        free_tz(tz); fclose(f); return -7;
    }

    /* 3. Зчитування структур ttinfo (4 байти utoff, 1 байт isdst, 1 байт desigidx) */
    for (uint32_t i = 0; i < h1.typecnt; ++i) {
        int32_t raw_utoff;
        uint8_t isdst, desigidx;
        if (fread(&raw_utoff, 4, 1, f) != 1 ||
            fread(&isdst, 1, 1, f) != 1 ||
            fread(&desigidx, 1, 1, f) != 1) {
            free_tz(tz); fclose(f); return -8;
        }
        tz->types[i].utoff = (int32_t)be32toh((uint32_t)raw_utoff);
        tz->types[i].isdst = isdst;
        tz->types[i].desigidx = desigidx;
    }

    /* 4. Зчитування таблиці назв та абревіатур */
    if (h1.charcnt > 0 && fread(tz->char_table, 1, h1.charcnt, f) != h1.charcnt) {
        free_tz(tz); fclose(f); return -9;
    }

    /* 5. Пропуск високосних записів та прапорців */
    long skip_rest = (long)h1.leapcnt * 12 + (long)h1.ttisstdcnt + (long)h1.ttisgmtcnt;
    fseek(f, skip_rest, SEEK_CUR);

    /* 6. Зчитування завершального рядка POSIX TZ */
    int c = fgetc(f);
    if (c == '\n') {
        size_t idx = 0;
        while ((c = fgetc(f)) != EOF && c != '\n' && idx < sizeof(tz->posix_tz) - 1) {
            tz->posix_tz[idx++] = (char)c;
        }
        tz->posix_tz[idx] = '\0';
    }

    fclose(f);
    return 0;
}

static const struct ttinfo* lookup_time(const struct parsed_tz *tz, int64_t target_time) {
    if (tz->timecnt == 0 || target_time < tz->transitions[0]) {
        /* Якщо переходів немає або час передує першому переходу:
           шукаємо перший тип без прапорця DST */
        for (uint32_t i = 0; i < tz->typecnt; ++i) {
            if (!tz->types[i].isdst) return &tz->types[i];
        }
        return tz->typecnt > 0 ? &tz->types[0] : NULL;
    }

    /* Двійковий пошук переходу, меншого або рівного target_time */
    int32_t left = 0, right = (int32_t)tz->timecnt - 1;
    int32_t best = 0;

    while (left <= right) {
        int32_t mid = left + (right - left) / 2;
        if (tz->transitions[mid] <= target_time) {
            best = mid;
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    uint8_t type_idx = tz->type_indices[best];
    if (type_idx < tz->typecnt) {
        return &tz->types[type_idx];
    }
    return NULL;
}

int main(int argc, char **argv) {
    const char *path = (argc > 1) ? argv[1] : "/etc/localtime";
    time_t now = time(NULL);

    struct parsed_tz tz;
    int err = parse_tzfile64(path, &tz);
    if (err != 0) {
        fprintf(stderr, "Помилка розбору tzfile (%s): код %d (%s)\n", path, err, strerror(errno));
        return 1;
    }

    const struct ttinfo *active = lookup_time(&tz, (int64_t)now);
    if (!active) {
        fprintf(stderr, "Не вдалося визначити активний тип часу.\n");
        free_tz(&tz);
        return 1;
    }

    const char *abbr = &tz.char_table[active->desigidx];
    int hours = active->utoff / 3600;
    int minutes = abs(active->utoff % 3600) / 60;

    printf("Файл часового поясу : %s\n", path);
    printf("Кількість переходів : %u\n", tz.timecnt);
    printf("Поточна мітка time_t: %ld (UTC)\n", (long)now);
    printf("Активне зміщення    : %+03d:%02d (%+d секунд)\n", hours, minutes, active->utoff);
    printf("Режим літнього часу : %s\n", active->isdst ? "ТАК (DST активний)" : "НІ (Стандартний час)");
    printf("Абревіатура зони    : %s\n", abbr);
    if (tz.posix_tz[0]) {
        printf("Правило POSIX TZ    : %s\n", tz.posix_tz);
    }

    free_tz(&tz);
    return 0;
}
```
```cpp
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
```
:::

## Підводні камені та інженерні тонкощі

1. **Порядок байтів (Endianness):** Усі лічильники заголовка та масиви переходів у `tzfile` завжди зберігаються у форматі Big-Endian. Пряме приведення вказівника типу `(int64_t*)buffer` на процесорах архітектури x86-64 або Little-Endian ARM призведе до зчитування псевдовипадкових значень через інверсію розташування байтів. Застосування `be64toh()` та `be32toh()` є строго обов'язковим для кожного числового поля.
2. **Знаковість зміщень:** Поле `utoff` є 32-бітним цілим числом зі знаком (`int32_t`). Для поясів на захід від Гринвіча (наприклад, `America/New_York` із базовим зміщенням UTC-5) величина зберігається як від'ємне число (`-18000`). Якщо помилково прочитати його як `uint32_t`, зміщення перетвориться на додатне число `4294949296`, що повністю зламає подальший розрахунок календарної дати.
3. **Обробка часу до першого переходу:** Якщо запитувана часова позначка `time_t` передує найпершому запису в масиві переходів (наприклад, історична дата кінця XIX століття), алгоритм не повинен аварійно завершуватися або повертати неініціалізовану пам'ять. Стандарт RFC 8536 прямо вимагає у такому разі брати перший дескриптор `ttinfo`, у якого прапорець літнього часу скинутий (`isdst == 0`).
4. **Вихід за межі таблиці та рядок POSIX TZ:** Останній зафіксований перехід у базі даних `tzdata` створюється компілятором `zic` лише на кілька десятиліть уперед від моменту збирання пакету, оскільки закони держав про переведення годинників можуть будь-коли змінитися. Для коректного обчислення дат у далекому майбутньому (наприклад, 2060 чи 2100 рік) системні бібліотеки використовують завершальний текстовий рядок POSIX TZ (наприклад, `EET-2EEST,M3.5.0/3,M10.5.0/4`). Він кодує періодичний алгоритм весняного й осіннього переходів без необхідності зберігати нескінченні бінарні масиви.
5. **Кешування дескриптора в бібліотеці C:** У системній бібліотеці `glibc` функція `localtime_r()` кешує прочитаний файл у статичних структурах процесу. Якщо адміністратор змінює символічне посилання `/etc/localtime` без перезапуску довготривалого демона, бібліотека виконує системний виклик `stat("/etc/localtime")` під час чергового виклику `localtime_r()` і перечитує файл лише тоді, коли змінився номер inode або час модифікації файлу.
