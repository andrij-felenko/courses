# ⚙️ Створення, інспектування та програмний аналіз образів EROFS

<preknowlist>
- [Модель inode](root:sys-unix/inode-model) — індексні вузли, метадані та відокремлення імен від вмісту.
- [Довідник дискових структур даних EROFS](root:sys-unix/erofs-read-only-filesystem/api-erofs-ondisk.md) — бінарні структури суперблоку та індексних вузлів.
</preknowlist>

Для створення, розбору, аналізу продуктивності та перевірки цілісності файлових систем EROFS використовується пакет інструментів простору користувача `erofs-utils`. У даному практичному керівництві розібрано повний цикл роботи з образом EROFS: від налаштування компресії під час збирання утилітою `mkfs.erofs` до низькорівневого аналізу бінарних структур мовами C та C++.

## Встановлення інструментарію та структура пакета

Пакет `erofs-utils` доступний у більшості дистрибутивів Linux або збирається з вихідних кодів окремого репозиторію `erofs-utils` на `git.kernel.org` — до дерева ядра він не входить. Утиліти включають наступні ключові бінарники:

- `mkfs.erofs`: Генератор дискового образу з вихідного дерева каталогів.
- `dump.erofs`: Аналізатор метаданих, таблиць екстентів та геометрії тома.
- `fsck.erofs`: Інструмент верифікації цілісності дискових структур та перевірки чексум; із ключем `--extract` ще й розпаковує образ у каталог.
- `erofsfuse`: Драйвер FUSE для монтування та читання образів EROFS у просторі користувача без прав суперкористувача.

Для встановлення утиліт у сучасних дистрибутивах використовуються стандартні пакетні менеджери:

```bash
# Ubuntu / Debian
sudo apt install erofs-utils

# Fedora / RHEL / CentOS
sudo dnf install erofs-utils

# Arch Linux
sudo pacman -S erofs-utils
```

## Збирання стисненого образу за допомогою mkfs.erofs

Утиліта `mkfs.erofs` формує готовий бінарний образ Read-Only з вихідної директорії. Залежно від цільового призначення образу (системний розділ смартфона, rootfs для мікро-VM або шар контейнера) розробник обирає компресор, рівень упаковки та параметри дедуплікації.

Під час збирання образу `mkfs.erofs` сканує дерево каталогів у двоетапному режимі: спочатку обчислюється оптимальне вирівнювання індексних вузлів та будується таблиця спільних розширених атрибутів, а на другому етапі виконується паралельне стиснення файлових екстентів.

```bash
# 1. Базове збирання з алгоритмом LZ4HC (оптимальний баланс швидкості декомпресії)
mkfs.erofs -z lz4hc,12 sys_image.erofs ./target_rootfs/

# 2. Збирання з максимальним стисненням Zstd та упаковкою хвостів файлів (ztailpacking)
mkfs.erofs -z zstd,9 -E ztailpacking sys_image_zstd.erofs ./target_rootfs/

# 3. Формування образу для контейнерного середовища з дедуплікацією (chunk-based)
mkfs.erofs --chunksize=65536 container_layer.erofs ./container_root/

# 4. Збирання з автоматичною індексацією та дедуплікацією атрибутів безпеки SELinux
mkfs.erofs -z lz4hc,9 --file-contexts=/etc/selinux/targeted/contexts/files/file_contexts android_sys.erofs ./android_sys/
```

### Розбір критичних параметрів mkfs.erofs

- `-z <algorithm>[,level]`: Обирає внутрішній алгоритм стиснення даних та рівень компресії:
  - `lz4` / `lz4hc`: Забезпечує найвищу швидкість декомпресії за місцем (In-place) із низьким навантаженням на CPU. Ідеально для системних розділів та мікро-VM.
  - `zstd`: Дає вищий коефіцієнт стиснення (економія диска додатково на 10–15%), але потребує дещо більше обчислювальних ресурсів процесора під час холодного читання.
  - `lzma` / `microlzma`: Застосовується для ультра-компактних прошивок вбудованих пристроїв.
- `-E ztailpacking`: Умикає інлайн-упаковку хвостового фізичного кластера **стисненого** файла (прапорець `EROFS_FEATURE_INCOMPAT_ZTAILPACKING`). Останній, неповний pcluster лягає не окремим блоком даних, а поруч із індексним вузлом у блоці метаданих. Для нестиснених файлів те саме робить типовий режим `EROFS_INODE_FLAT_INLINE`, і окремого ключа він не потребує.
- `-C <size>`: Задає розмір фізичного кластера стиснення (pcluster size). За замовчуванням дорівнює 4096 байтам (`4KB`), що збігається з розміром сторінки пам'яті архітектури.
- `--file-contexts`: Вказує шлях до конфігурації SELinux. `mkfs.erofs` парсить текстові мітки безпеки та конвертує їх у глобальну індексовану таблицю спільних атрибутів (`shared xattr table`).

## Інспектування та перевірка цілісності образів

Після збирання образу інженер може перевірити дискову геометрію, ефективність стиснення та цілісність індексних вузлів за допомогою утиліт `dump.erofs` та `fsck.erofs`.

Утиліта `dump.erofs` дозволяє витягнути будь-які низькорівневі параметри дискового образу без його монтування в систему, що робить її незамінною для CI/CD автоматизації перевірки контейнерних образів.

```bash
# Вивід загальної інформації про суперблок та прапорці несумісності
dump.erofs -s sys_image.erofs

# Детальна статистика розподілу типів файлів, розмірів та коефіцієнта стиснення
dump.erofs -S sys_image.erofs

# Вивід карти екстентів для конкретного файла за його NID або шляхом
dump.erofs --path=/usr/lib/libc.so sys_image.erofs

# Повна перевірка цілісності всіх індексних вузлів та обчислення чексум
fsck.erofs sys_image.erofs
```

Приклад виводу утиліти `dump.erofs -S`:

```
Filesystem magic number:                      0xE0F5E1E2
Filesystem block size:                        4096
Filesystem total blocks:                      131072
Filesystem inode count:                       14250
Filesystem shared xattrs count:               42
Filesystem compression algorithm:             lz4hc
Filesystem average compression ratio:         48.25%
```

## Монтування та інспектування через sysfs ядра

В ядрі Linux монтування EROFS здійснюється стандартною командою `mount` із вказівкою типу файлової системи `erofs`:

```bash
# Монтування образу через loop-пристрій у режимі лише для читання
sudo mount -t erofs -o loop sys_image.erofs /mnt/system

# Перевірка параметрів монтування у /proc/mounts
cat /proc/mounts | grep erofs
```

Після монтування ядро Linux експортує діагностичні інтерфейси підсистеми EROFS у віртуальну файлову систему `/sys/fs/erofs/`. Ці інтерфейси дозволяють відстежувати статистику декомпресії та активні параметри ядерного драйвера:

```bash
# Які розширення дискового формату розуміє поточне ядро
ls /sys/fs/erofs/features/

# Режим синхронної декомпресії для змонтованого пристрою
cat /sys/fs/erofs/loop0/sync_decompress
```

## Програмний аналіз суперблоку та індексних вузлів

Для глибокого розуміння дискового формату нижче наведено реалізацію утиліти розбору суперблоку EROFS. Програма відкриває образ, виконує позиціонування на зсув 1024 байти, читає структуру `erofs_super_block`, перевіряє сигнатуру `0xE0F5E1E2`, розраховує розмір блоку та адресу кореневого індексного вузла.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

#define EROFS_SUPER_MAGIC  0xE0F5E1E2
#define EROFS_SUPER_OFFSET 1024

#pragma pack(push, 1)
struct erofs_super_block_raw {
    uint32_t magic;
    uint32_t checksum;
    uint32_t feature_compat;
    uint8_t  blkszbits;
    uint8_t  sb_extslots;
    uint16_t root_nid;
    uint64_t inos;
    uint64_t build_time;
    uint32_t build_time_nsec;
    uint32_t blocks;
    uint32_t meta_blkaddr;
    uint32_t xattr_blkaddr;
    uint8_t  uuid[16];
    uint8_t  volume_name[16];
    uint32_t feature_incompat;
};
#pragma pack(pop)

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <path_to_erofs_img>\n", argv[0]);
        return 1;
    }

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити файл образу EROFS");
        return 1;
    }

    if (lseek(fd, EROFS_SUPER_OFFSET, SEEK_SET) != EROFS_SUPER_OFFSET) {
        perror("Помилка позиціонування lseek");
        close(fd);
        return 1;
    }

    struct erofs_super_block_raw sb;
    ssize_t res = read(fd, &sb, sizeof(sb));
    if (res != (ssize_t)sizeof(sb)) {
        perror("Помилка зчитування суперблоку");
        close(fd);
        return 1;
    }

    close(fd);

    if (sb.magic != EROFS_SUPER_MAGIC) {
        fprintf(stderr, "Помилка: некоректна сигнатура EROFS (0x%X != 0x%X)\n",
                sb.magic, EROFS_SUPER_MAGIC);
        return 1;
    }

    uint32_t block_size = 1U << sb.blkszbits;
    uint64_t total_bytes = (uint64_t)sb.blocks * block_size;
    uint64_t root_nid_offset = (uint64_t)sb.meta_blkaddr * block_size + (uint64_t)sb.root_nid * 32;

    printf("=== Метадані EROFS Суперблоку (C) ===\n");
    printf("Сигнатура Magic     : 0x%X (Успішно)\n", sb.magic);
    printf("Розмір блоку        : %u байт (blkszbits: %u)\n", block_size, sb.blkszbits);
    printf("Загалом блоків      : %u (%llu байт)\n", sb.blocks, (unsigned long long)total_bytes);
    printf("Адреса метаданих    : блок %u (зсув %llu B)\n",
           sb.meta_blkaddr, (unsigned long long)sb.meta_blkaddr * block_size);
    printf("Кореневий NID       : %u (зсув кореневого inode: %llu B)\n",
           sb.root_nid, (unsigned long long)root_nid_offset);
    printf("Прапорці incompat   : 0x%X\n", sb.feature_incompat);

    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <cstdint>
#include <expected>
#include <string_view>
#include <iomanip>
#include <span>

constexpr uint32_t EROFS_SUPER_MAGIC = 0xE0F5E1E2;
constexpr std::streamoff EROFS_SUPER_OFFSET = 1024;

#pragma pack(push, 1)
struct ErofsSuperBlockRaw {
    uint32_t magic;
    uint32_t checksum;
    uint32_t feature_compat;
    uint8_t  blkszbits;
    uint8_t  sb_extslots;
    uint16_t root_nid;
    uint64_t inos;
    uint64_t build_time;
    uint32_t build_time_nsec;
    uint32_t blocks;
    uint32_t meta_blkaddr;
    uint32_t xattr_blkaddr;
    uint8_t  uuid[16];
    uint8_t  volume_name[16];
    uint32_t feature_incompat;
};
#pragma pack(pop)

struct ErofsParsedInfo {
    uint32_t magic;
    uint32_t block_size;
    uint32_t total_blocks;
    uint64_t total_bytes;
    uint32_t meta_block_addr;
    uint16_t root_nid;
    uint64_t root_inode_offset;
    uint32_t feature_incompat;
};

std::expected<ErofsParsedInfo, std::string> parse_erofs_image(const std::string& image_path) {
    std::ifstream file(image_path, std::ios::binary);
    if (!file.is_open()) {
        return std::unexpected("Не вдалося відкрити файл образу EROFS");
    }

    file.seekg(EROFS_SUPER_OFFSET, std::ios::beg);
    if (!file.good()) {
        return std::unexpected("Помилка позиціонування у файлі образу");
    }

    ErofsSuperBlockRaw sb{};
    file.read(reinterpret_cast<char*>(&sb), sizeof(sb));
    if (file.gcount() != static_cast<std::streamsize>(sizeof(sb))) {
        return std::unexpected("Не вдалося зчитати повну структуру суперблоку");
    }

    if (sb.magic != EROFS_SUPER_MAGIC) {
        return std::unexpected("Некоректний Magic ID: файл не є образом EROFS");
    }

    uint32_t block_sz = 1U << sb.blkszbits;
    uint64_t total_sz = static_cast<uint64_t>(sb.blocks) * block_sz;
    uint64_t root_offset = static_cast<uint64_t>(sb.meta_blkaddr) * block_sz + static_cast<uint64_t>(sb.root_nid) * 32;

    return ErofsParsedInfo{
        .magic = sb.magic,
        .block_size = block_sz,
        .total_blocks = sb.blocks,
        .total_bytes = total_sz,
        .meta_block_addr = sb.meta_blkaddr,
        .root_nid = sb.root_nid,
        .root_inode_offset = root_offset,
        .feature_incompat = sb.feature_incompat
    };
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <path_to_erofs_img>\n";
        return 1;
    }

    auto result = parse_erofs_image(argv[1]);
    if (!result) {
        std::cerr << "Помилка аналізу: " << result.error() << "\n";
        return 1;
    }

    const auto& info = result.value();
    std::cout << "=== Метадані EROFS Суперблоку (C++ RAII) ===\n"
              << "Сигнатура Magic     : 0x" << std::hex << std::uppercase << info.magic << std::dec << " (Успішно)\n"
              << "Розмір блоку        : " << info.block_size << " байт\n"
              << "Загалом блоків      : " << info.total_blocks << " (" << info.total_bytes << " B)\n"
              << "Адреса метаданих    : блок " << info.meta_block_addr << "\n"
              << "Кореневий NID       : " << info.root_nid << "\n"
              << "Зсув кореневого inode: " << info.root_inode_offset << " байт\n"
              << "Прапорці incompat   : 0x" << std::hex << info.feature_incompat << std::dec << "\n";

    return 0;
}
```
:::

### Детальний аналіз реалізації та інваріантів безпеки

Обидва варіанти програми реалізують сувору перевірку інваріантів безпеки дискового формату:

1. **#pragma pack(push, 1)**: Усі бінарні структури ядра Linux упаковані без автоматичного вирівнювання заповненням (padding) між полями. Директива упакування гарантує, що поля лягають рівно на дискові зсуви; сама структура покриває перші 84 байти зі 128-байтового суперблоку, решту — резерв — ця програма не читає.
2. **Перевірка Magic ID**: Сигнатура `0xE0F5E1E2` (Little Endian) гарантує, що розібраний файл є образом EROFS, а не образом ext4 чи SquashFS.
3. **Обчислення адреси NID**: Ідентифікатор NID (Node Identifier) у EROFS описує зсув індексного вузла у блоках метаданих у 32-байтових одиницях. Формула `(meta_blkaddr * block_size) + (root_nid * 32)` розраховує точний абсолютний байтовий зсув кореневого inode від початку образу.
4. **C++ RAII та std::expected**: Версія мовою C++ демонструє сучасний ідіоматичний підхід: потік `std::ifstream` автоматично закриває файловий дескриптор при виході з області видимості, а повертаний тип `std::expected<ErofsParsedInfo, std::string>` безпечно обробляє помилки відкриття та читання без використання винятків або небезпечного коду з `goto out`.
