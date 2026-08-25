# ⚙️ Реалізація зчитувача файлової системи FAT32

Цей проєкт демонструє створення повнофункціонального автономного зчитувача образів файлової системи FAT32 мовами C та C++, здатного монтувати двійковий дамп накопичувача, розпізнавати параметри BPB, розгортати ієрархію каталогів з довгими іменами (VFAT LFN) та витягувати вміст файлів шляхом обходу ланцюжків кластерів.

---

## 1. Архітектура та послідовність роботи парсера

Щоб прочитати довільний файл з незмонтованого блочного носія FAT32 (наприклад, дампу SD-картки або розділу диска), програма повинна безпосередньо взаємодіяти з двійковими структурами на диску без залучення системних викликів ядра ОС. Парсер реалізує повний цикл роботи з файловою системою в просторі користувача.

Уся навігація по файловій системі будується як кінцевий автомат, що послідовно проходить такі фази:

1. **Валідація та зчитування BPB:** З нульового сектора зчитується структура `FAT32_BootSector`. Перевіряються сигнатури (`0xAA55`), розмір сектора та ненульовий розмір кластера. Якщо сигнатура не збігається або розмір сектора не дорівнює 512/1024/2048/4096 байтів, монтування негайно переривається з помилкою.
2. **Розрахунок базових адрес:** Обчислюються зміщення початку таблиці FAT, початок області даних (`FirstDataSector`) та розмір кластера в байтах. Усі зміщення приводяться до абсолютних байтових координат у файлі образу або номерів секторів LBA.
3. **Обхід кореневого каталогу:** Починаючи з кластера `BPB_RootClus` (зазвичай кластер 2), зчитуються 32-байтні записи каталогу. Якщо каталог займає кілька кластерів, парсер відстежує ланцюжок через таблицю FAT так само, як для звичайного файлу.
4. **Акумуляція довгих імен (LFN):** Якщо зустрічаються записи з атрибутом `0x0F`, їхні символи UTF-16LE збираються в буфер у зворотному порядку, поки не зустрінеться цільовий запис SFN з контрольною сумою.
5. **Пошук цільового шляху:** Ім'я порівнюється з шуканим файлом. Якщо знайдено підкаталог — переходимо в його початковий кластер і повторюємо сканування; якщо файл — переходимо до зчитування даних.
6. **Зчитування ланцюжка кластерів:** Зчитуються байти кластера, після чого в таблиці FAT шукається номер наступного кластера, доки не зустрінеться маркер `0x0FFFFFF8`..`0x0FFFFFFF` (EOC).

---

## 2. Реалізація базового зчитувача FAT32

Нижче наведено робочий код мовами C та C++. Обидва варіанти демонструють ідентичний алгоритм, але використовують ідіоматичні засоби кожної з мов: у C — явні покажчики, ручне виділення динамічної пам'яті через `malloc`/`free` та стандартний ввід-вивід `fopen`/`fread`; у C++ — класи RAII, безпечні представлення `std::span` та `std::string_view`, контейнери `std::vector` і потоки `std::ifstream`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#pragma pack(push, 1)
typedef struct {
    uint8_t  BS_jmpBoot[3];
    char     BS_OEMName[8];
    uint16_t BPB_BytsPerSec;
    uint8_t  BPB_SecPerClus;
    uint16_t BPB_RsvdSecCnt;
    uint8_t  BPB_NumFATs;
    uint16_t BPB_RootEntCnt;
    uint16_t BPB_TotSec16;
    uint8_t  BPB_Media;
    uint16_t BPB_FATSz16;
    uint16_t BPB_SecPerTrk;
    uint16_t BPB_NumHeads;
    uint32_t BPB_HiddSec;
    uint32_t BPB_TotSec32;
    uint32_t BPB_FATSz32;
    uint16_t BPB_ExtFlags;
    uint16_t BPB_FSVer;
    uint32_t BPB_RootClus;
    uint16_t BPB_FSInfo;
    uint16_t BPB_BkBootSec;
    uint8_t  BPB_Reserved[12];
    uint8_t  BS_DrvNum;
    uint8_t  BS_Reserved1;
    uint8_t  BS_BootSig;
    uint32_t BS_VolID;
    char     BS_VolLab[11];
    char     BS_FilSysType[8];
    uint8_t  BS_BootCode[420];
    uint16_t BS_Signature;
} FAT32_BS;

typedef struct {
    char     DIR_Name[8];
    char     DIR_Ext[3];
    uint8_t  DIR_Attr;
    uint8_t  DIR_NTRes;
    uint8_t  DIR_CrtTimeTenth;
    uint16_t DIR_CrtTime;
    uint16_t DIR_CrtDate;
    uint16_t DIR_LstAccDate;
    uint16_t DIR_FstClusHI;
    uint16_t DIR_WrtTime;
    uint16_t DIR_WrtDate;
    uint16_t DIR_FstClusLO;
    uint32_t DIR_FileSize;
} FAT_Dir;

typedef struct {
    uint8_t  LDIR_Ord;
    uint16_t LDIR_Name1[5];
    uint8_t  LDIR_Attr;
    uint8_t  LDIR_Type;
    uint8_t  LDIR_Chksum;
    uint16_t LDIR_Name2[6];
    uint16_t LDIR_FstClusLO;
    uint16_t LDIR_Name3[2];
} FAT_LFN;
#pragma pack(pop)

typedef struct {
    FILE      *file;
    FAT32_BS   bs;
    uint32_t   fat_start_lba;
    uint32_t   data_start_lba;
    uint32_t   bytes_per_clus;
} FAT32_Context;

/* Розрахунок контрольної суми короткого імені 8.3 */
static uint8_t calc_sfn_checksum(const uint8_t *sfn_name) {
    uint8_t sum = 0;
    for (int i = 0; i < 11; i++) {
        sum = ((sum & 1) ? 0x80 : 0) + (sum >> 1) + sfn_name[i];
    }
    return sum;
}

/* Ініціалізація контексту FAT32 */
bool fat32_init(FAT32_Context *ctx, const char *image_path) {
    ctx->file = fopen(image_path, "rb");
    if (!ctx->file) return false;

    if (fread(&ctx->bs, sizeof(FAT32_BS), 1, ctx->file) != 1) {
        fclose(ctx->file);
        return false;
    }

    if (ctx->bs.BS_Signature != 0xAA55 || ctx->bs.BPB_BytsPerSec == 0) {
        fclose(ctx->file);
        return false;
    }

    ctx->fat_start_lba = ctx->bs.BPB_RsvdSecCnt;
    ctx->data_start_lba = ctx->bs.BPB_RsvdSecCnt + (ctx->bs.BPB_NumFATs * ctx->bs.BPB_FATSz32);
    ctx->bytes_per_clus = (uint32_t)ctx->bs.BPB_BytsPerSec * ctx->bs.BPB_SecPerClus;
    return true;
}

void fat32_close(FAT32_Context *ctx) {
    if (ctx->file) {
        fclose(ctx->file);
        ctx->file = NULL;
    }
}

/* Перетворення номера кластера у фізичний LBA сектор */
static uint32_t cluster_to_lba(const FAT32_Context *ctx, uint32_t cluster) {
    return ctx->data_start_lba + (cluster - 2) * ctx->bs.BPB_SecPerClus;
}

/* Зчитування наступного кластера з таблиці FAT */
static uint32_t fat32_next_cluster(FAT32_Context *ctx, uint32_t current_cluster) {
    uint32_t fat_offset = current_cluster * 4;
    uint32_t fat_sec = ctx->fat_start_lba + (fat_offset / ctx->bs.BPB_BytsPerSec);
    uint32_t ent_offset = fat_offset % ctx->bs.BPB_BytsPerSec;

    long byte_pos = (long)fat_sec * ctx->bs.BPB_BytsPerSec + ent_offset;
    if (fseek(ctx->file, byte_pos, SEEK_SET) != 0) return 0x0FFFFFFF;

    uint32_t next_entry = 0;
    if (fread(&next_entry, sizeof(uint32_t), 1, ctx->file) != 1) return 0x0FFFFFFF;

    return next_entry & 0x0FFFFFFF; /* Ігноруємо старші 4 зарезервовані біти */
}

/* Зчитування повного кластера даних у пам'ять */
bool fat32_read_cluster(FAT32_Context *ctx, uint32_t cluster, uint8_t *buffer) {
    uint32_t lba = cluster_to_lba(ctx, cluster);
    long byte_pos = (long)lba * ctx->bs.BPB_BytsPerSec;

    if (fseek(ctx->file, byte_pos, SEEK_SET) != 0) return false;
    return fread(buffer, ctx->bytes_per_clus, 1, ctx->file) == 1;
}

/* Виведення вмісту кореневого каталогу та зчитування цільового файлу */
void fat32_list_root(FAT32_Context *ctx) {
    uint8_t *clus_buf = (uint8_t*)malloc(ctx->bytes_per_clus);
    if (!clus_buf) return;

    uint32_t curr_clus = ctx->bs.BPB_RootClus;
    char lfn_buf[256] = {0};
    int lfn_chars = 0;
    uint8_t expected_chksum = 0;

    while (curr_clus < 0x0FFFFFF8 && curr_clus >= 2) {
        if (!fat32_read_cluster(ctx, curr_clus, clus_buf)) break;

        FAT_Dir *entries = (FAT_Dir*)clus_buf;
        size_t count = ctx->bytes_per_clus / sizeof(FAT_Dir);

        for (size_t i = 0; i < count; i++) {
            FAT_Dir *entry = &entries[i];

            if ((uint8_t)entry->DIR_Name[0] == 0x00) {
                /* Більше дійсних записів у каталозі немає */
                free(clus_buf);
                return;
            }
            if ((uint8_t)entry->DIR_Name[0] == 0xE5) {
                lfn_chars = 0;
                continue; /* Вилучений запис */
            }

            if (entry->DIR_Attr == 0x0F) {
                /* Запис VFAT LFN */
                FAT_LFN *lfn = (FAT_LFN*)entry;
                expected_chksum = lfn->LDIR_Chksum;

                /* Декодуємо 13 символів UTF-16LE в ASCII/UTF-8 */
                uint16_t chars16[13];
                memcpy(&chars16[0], lfn->LDIR_Name1, 10);
                memcpy(&chars16[5], lfn->LDIR_Name2, 12);
                memcpy(&chars16[11], lfn->LDIR_Name3, 4);

                int seq = (lfn->LDIR_Ord & 0x1F) - 1;
                for (int c = 0; c < 13; c++) {
                    if (chars16[c] == 0x0000 || chars16[c] == 0xFFFF) break;
                    if (seq * 13 + c < 255) {
                        lfn_buf[seq * 13 + c] = (char)(chars16[c] & 0xFF);
                        if (seq * 13 + c >= lfn_chars) lfn_chars = seq * 13 + c + 1;
                    }
                }
                continue;
            }

            /* Стандартний запис SFN 8.3 */
            if (entry->DIR_Attr & 0x08) {
                lfn_chars = 0;
                continue; /* Пропускаємо мітку тома */
            }

            lfn_buf[lfn_chars] = '\0';
            uint8_t actual_chksum = calc_sfn_checksum((uint8_t*)entry->DIR_Name);
            const char *display_name = (lfn_chars > 0 && expected_chksum == actual_chksum) ? lfn_buf : entry->DIR_Name;

            uint32_t first_clus = ((uint32_t)entry->DIR_FstClusHI << 16) | entry->DIR_FstClusLO;
            bool is_dir = (entry->DIR_Attr & 0x10) != 0;

            printf("[%s] %-24s | Кластер: %-6u | Розмір: %u байтів\n",
                   is_dir ? "DIR " : "FILE", display_name, first_clus, entry->DIR_FileSize);

            lfn_chars = 0;
        }

        curr_clus = fat32_next_cluster(ctx, curr_clus);
    }

    free(clus_buf);
}
```
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <cstdint>
#include <cstring>
#include <optional>

namespace fat32 {

#pragma pack(push, 1)
struct alignas(1) BootSector {
    uint8_t  jmpBoot[3];
    char     oemName[8];
    uint16_t bytesPerSector;
    uint8_t  sectorsPerCluster;
    uint16_t reservedSectorCount;
    uint8_t  numFATs;
    uint16_t rootEntryCount;
    uint16_t totalSectors16;
    uint8_t  mediaType;
    uint16_t fatSize16;
    uint16_t sectorsPerTrack;
    uint16_t headCount;
    uint32_t hiddenSectors;
    uint32_t totalSectors32;
    uint32_t fatSize32;
    uint16_t extFlags;
    uint16_t fsVersion;
    uint32_t rootCluster;
    uint16_t fsInfoSector;
    uint16_t backupBootSector;
    uint8_t  reserved[12];
    uint8_t  driveNumber;
    uint8_t  reserved1;
    uint8_t  bootSignature;
    uint32_t volumeID;
    char     volumeLabel[11];
    char     fileSystemType[8];
    uint8_t  bootCode[420];
    uint16_t signature;
};

struct alignas(1) DirEntry {
    char     name[8];
    char     ext[3];
    uint8_t  attributes;
    uint8_t  ntReserved;
    uint8_t  creationTimeTenth;
    uint16_t creationTime;
    uint16_t creationDate;
    uint16_t lastAccessDate;
    uint16_t firstClusterHigh;
    uint16_t writeTime;
    uint16_t writeDate;
    uint16_t firstClusterLow;
    uint32_t fileSize;

    [[nodiscard]] constexpr uint32_t firstCluster() const noexcept {
        return (static_cast<uint32_t>(firstClusterHigh) << 16) | firstClusterLow;
    }
    [[nodiscard]] constexpr bool isDirectory() const noexcept { return (attributes & 0x10) != 0; }
    [[nodiscard]] constexpr bool isLFN() const noexcept { return (attributes & 0x0F) == 0x0F; }
    [[nodiscard]] constexpr bool isVolumeLabel() const noexcept { return (attributes & 0x08) != 0; }
    [[nodiscard]] constexpr bool isDeleted() const noexcept { return static_cast<uint8_t>(name[0]) == 0xE5; }
    [[nodiscard]] constexpr bool isEndOfDir() const noexcept { return static_cast<uint8_t>(name[0]) == 0x00; }
};

struct alignas(1) LFNEntry {
    uint8_t  order;
    uint16_t name1[5];
    uint8_t  attributes;
    uint8_t  type;
    uint8_t  checksum;
    uint16_t name2[6];
    uint16_t firstClusterLow;
    uint16_t name3[2];
};
#pragma pack(pop)

class ImageReader {
public:
    explicit ImageReader(const std::string& path) {
        stream_.open(path, std::ios::binary);
    }

    [[nodiscard]] bool isOpen() const noexcept { return stream_.is_open(); }

    bool readAt(uint64_t offset, std::span<uint8_t> buffer) {
        stream_.seekg(static_cast<std::streamoff>(offset), std::ios::beg);
        stream_.read(reinterpret_cast<char*>(buffer.data()), buffer.size());
        return stream_.gcount() == static_cast<std::streamsize>(buffer.size());
    }

private:
    std::ifstream stream_;
};

class Volume {
public:
    static std::optional<Volume> mount(const std::string& imagePath) {
        auto reader = std::make_unique<ImageReader>(imagePath);
        if (!reader->isOpen()) return std::nullopt;

        BootSector bs{};
        if (!reader->readAt(0, {reinterpret_cast<uint8_t*>(&bs), sizeof(BootSector)})) {
            return std::nullopt;
        }

        if (bs.signature != 0xAA55 || bs.bytesPerSector == 0 || bs.sectorsPerCluster == 0) {
            return std::nullopt;
        }

        return Volume(std::move(reader), bs);
    }

    void listRootDirectory() {
        uint32_t clusterBytes = static_cast<uint32_t>(bs_.bytesPerSector) * bs_.sectorsPerCluster;
        std::vector<uint8_t> clusterBuffer(clusterBytes);

        uint32_t currentCluster = bs_.rootCluster;
        std::string lfnBuffer;
        uint8_t expectedChecksum = 0;

        while (currentCluster >= 2 && currentCluster < 0x0FFFFFF8) {
            if (!readCluster(currentCluster, clusterBuffer)) break;

            auto entries = std::span<const DirEntry>(
                reinterpret_cast<const DirEntry*>(clusterBuffer.data()),
                clusterBytes / sizeof(DirEntry)
            );

            for (const auto& entry : entries) {
                if (entry.isEndOfDir()) return;
                if (entry.isDeleted()) {
                    lfnBuffer.clear();
                    continue;
                }

                if (entry.isLFN()) {
                    const auto& lfn = reinterpret_cast<const LFNEntry&>(entry);
                    expectedChecksum = lfn.checksum;

                    uint16_t rawChars[13];
                    std::memcpy(&rawChars[0], lfn.name1, 10);
                    std::memcpy(&rawChars[5], lfn.name2, 12);
                    std::memcpy(&rawChars[11], lfn.name3, 4);

                    std::string chunk;
                    for (uint16_t ch : rawChars) {
                        if (ch == 0x0000 || ch == 0xFFFF) break;
                        chunk.push_back(static_cast<char>(ch & 0xFF));
                    }
                    lfnBuffer = chunk + lfnBuffer;
                    continue;
                }

                if (entry.isVolumeLabel()) {
                    lfnBuffer.clear();
                    continue;
                }

                uint8_t actualChecksum = computeSFNChecksum(entry.name);
                std::string displayName = (!lfnBuffer.empty() && actualChecksum == expectedChecksum)
                                          ? lfnBuffer : extractSFN(entry);

                std::cout << (entry.isDirectory() ? "[DIR ] " : "[FILE] ")
                          << displayName << " | Кластер: " << entry.firstCluster()
                          << " | Розмір: " << entry.fileSize << " B\n";

                lfnBuffer.clear();
            }

            currentCluster = nextCluster(currentCluster);
        }
    }

private:
    Volume(std::unique_ptr<ImageReader> reader, const BootSector& bs)
        : reader_(std::move(reader)), bs_(bs) {
        fatStartLBA_ = bs_.reservedSectorCount;
        dataStartLBA_ = bs_.reservedSectorCount + (bs_.numFATs * bs_.fatSize32);
    }

    [[nodiscard]] uint32_t clusterToLBA(uint32_t cluster) const noexcept {
        return dataStartLBA_ + (cluster - 2) * bs_.sectorsPerCluster;
    }

    [[nodiscard]] uint32_t nextCluster(uint32_t currentCluster) {
        uint32_t fatOffset = currentCluster * 4;
        uint64_t byteOffset = static_cast<uint64_t>(fatStartLBA_) * bs_.bytesPerSector + fatOffset;

        uint32_t nextEntry = 0;
        if (!reader_->readAt(byteOffset, {reinterpret_cast<uint8_t*>(&nextEntry), sizeof(uint32_t)})) {
            return 0x0FFFFFFF;
        }
        return nextEntry & 0x0FFFFFFF;
    }

    bool readCluster(uint32_t cluster, std::span<uint8_t> buffer) {
        uint64_t byteOffset = static_cast<uint64_t>(clusterToLBA(cluster)) * bs_.bytesPerSector;
        return reader_->readAt(byteOffset, buffer);
    }

    static uint8_t computeSFNChecksum(const char name[8]) noexcept {
        uint8_t sum = 0;
        const auto* ptr = reinterpret_cast<const uint8_t*>(name);
        for (size_t i = 0; i < 11; ++i) {
            sum = static_cast<uint8_t>(((sum & 1) ? 0x80 : 0) + (sum >> 1) + ptr[i]);
        }
        return sum;
    }

    static std::string extractSFN(const DirEntry& entry) {
        std::string sfn;
        for (int i = 0; i < 8 && entry.name[i] != ' '; ++i) sfn.push_back(entry.name[i]);
        if (entry.ext[0] != ' ') {
            sfn.push_back('.');
            for (int i = 0; i < 3 && entry.ext[i] != ' '; ++i) sfn.push_back(entry.ext[i]);
        }
        return sfn;
    }

    std::unique_ptr<ImageReader> reader_;
    BootSector bs_;
    uint32_t fatStartLBA_{0};
    uint32_t dataStartLBA_{0};
};

} // namespace fat32
```
:::

---

## 3. Детальний аналіз критичних ділянок коду

### 3.1. Акумуляція довгих імен у зворотному порядку

Оскільки файлова система VFAT записує фрагменти довгого імені перед коротким записом у зворотному порядку, парсер зобов'язаний накопичувати байти за порядковими номерами `LDIR_Ord`. У функції на мові C ми використовуємо пряме індексування буфера:

```
int seq = (lfn->LDIR_Ord & 0x1F) - 1;
for (int c = 0; c < 13; c++) {
    lfn_buf[seq * 13 + c] = (char)(chars16[c] & 0xFF);
}
```

У C++ реалізації застосовується конкатенація рядкових фрагментів спереду: `lfnBuffer = chunk + lfnBuffer`. Прапорець `LAST_LONG_ENTRY` (`0x40`) сигналізує про те, що це перший за порядком читання запис, який відповідає фізичному хвосту довгого імені.

### 3.2. Маскування 28-бітних записів таблиці FAT32

У функції `fat32_next_cluster` операція `next_entry & 0x0FFFFFFF` відсікає 4 старші біти. Це критично, оскільки багато утиліт форматування залишають у цих бітах системні прапорці або сміття. Без маскування будь-який кластер із встановленим старшим бітом сприйматиметься як маркер кінця файлу або призведе до виходу за межі пам'яті.

---

## 4. Покрокове простеження читання файлу на практичному прикладі

Розглянемо практичний сценарій зчитування файлу `REPORT.PDF` розміром 9500 байтів, розміщеного в корені розділу FAT32.

1. **Монтування тома:** Парсер зчитує BPB і отримує такі параметри:
   - Розмір сектора `BytsPerSec = 512`;
   - Секторів у кластері `SecPerClus = 8` (розмір кластера = 4096 байтів);
   - Зарезервовано секторів `RsvdSecCnt = 32`;
   - Таблиць FAT `NumFATs = 2`, розмір таблиці `FATSz32 = 1024` сектори;
   - Початковий кластер кореневого каталогу `RootClus = 2`.
2. **Розрахунок старту даних:**
   - Початок таблиці FAT: сектор 32;
   - Початок купи даних: `FirstDataSector = 32 + (2 · 1024) = 2080`.
3. **Зчитування каталогу:** Парсер зчитує кластер 2, який відповідає фізичному сектору `LBA = 2080 + (2 - 2) · 8 = 2080`. Скануючи 32-байтні записи, парсер знаходить запис `REPORT  PDF`, де вказано:
   - Початковий кластер: `DIR_FstClusHI = 0x0000`, `DIR_FstClusLO = 0x0005` (кластер 5);
   - Розмір файлу: 9500 байтів.
4. **Обхід ланцюжка кластерів:**
   - **Кластер 5:** Перший сектор `LBA = 2080 + (5 - 2) · 8 = 2104`. Парсер зчитує 4096 байтів (зміщення файлу 0–4095).
   - Звернення до таблиці FAT: за зміщенням `5 · 4 = 20` байтів у секторі 32 зчитується значення `0x00000009`.
   - **Кластер 9:** Перший сектор `LBA = 2080 + (9 - 2) · 8 = 2136`. Парсер зчитує 4096 байтів (зміщення 4096–8191).
   - Звернення до таблиці FAT: за зміщенням `9 · 4 = 36` байтів зчитується значення `0x0000000C`.
   - **Кластер 12:** Перший сектор `LBA = 2080 + (12 - 2) · 8 = 2160`. Оскільки залишилося зчитати лише `9500 - 8192 = 1308` байтів, парсер читає залишок і зупиняється.
   - Звернення до таблиці FAT: за зміщенням `12 · 4 = 48` байтів зчитується маркер `0x0FFFFFFF` (EOC), що підтверджує коректне завершення файлу.

---

## 5. Безпека парсингу та захист від зловмисних дампів

Під час створення драйверів простору користувача або парсерів для вбудованих пристроїв критично важливо захистити код від навмисно пошкоджених файлових образів:

1. **Захист від 64-бітних переповнень адреси:** Під час обчислення байтового зміщення `(long)lba * BytsPerSec` на великих накопичувачах (понад 4 ГБ) 32-бітне ціле переповнюється. Усі проміжні розрахунки адрес обов'язково приводяться до типу `uint64_t`.
2. **Перевірка ділення на нуль:** Значення `BPB_BytsPerSec` та `BPB_SecPerClus` перевіряються на рівність нулю перед будь-якими операціями ділення чи взяття залишку.
3. **Виявлення циклів у таблиці FAT:** Зловмисний або пошкоджений образ може містити кільцевий ланцюжок (наприклад, кластер 5 вказує на 6, а 6 — знову на 5). Парсер зобов'язаний вести лічильник пройдених кластерів і припиняти обхід, якщо кількість кроків перевищує `CountOfClusters`.
4. **Валідація діапазону кластерів:** Номер кластера, отриманий із таблиці FAT, перед кожним зверненням до диска перевіряється на умову `2 <= cluster < CountOfClusters + 2`.
