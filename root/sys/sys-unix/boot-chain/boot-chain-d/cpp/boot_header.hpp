// Протокол завантаження Linux/x86: читання й заповнення setup_header.
// Помилки їдуть у std::expected, образ живе в об'єкті, а не в купці полів.
#pragma once

#include <cstdint>
#include <expected>
#include <filesystem>
#include <string>
#include <string_view>
#include <utility>

namespace boot {

inline constexpr std::streamoff kHeaderOffset = 0x01F1;
inline constexpr std::uint32_t  kHeaderMagic  = 0x53726448;  // "HdrS"
inline constexpr std::uint16_t  kBootFlag     = 0xAA55;
inline constexpr std::uint16_t  kProtoMin     = 0x0202;  // з'явився cmd_line_ptr
inline constexpr std::uint16_t  kProtoAddrMax = 0x0203;  // з'явився initrd_addr_max
inline constexpr std::uint32_t  kInitrdAddrMaxDefault = 0x37FFFFFF;

inline constexpr std::uint8_t kLoaderUnknown = 0xFF;
inline constexpr std::uint8_t kLoadedHigh    = 0x01;
inline constexpr std::uint8_t kQuietFlag     = 0x20;
inline constexpr std::uint8_t kCanUseHeap    = 0x80;

struct [[gnu::packed]] SetupHeader {
    std::uint8_t  setup_sects;      // Кількість секторів коду налаштування
    std::uint16_t root_flags;       // Прапорці монтування кореня (1 = read-only)
    std::uint32_t syssize;          // Розмір захищеного коду в 16-байтних параграфах
    std::uint16_t ram_size;         // Застаріле поле розміру пам'яті
    std::uint16_t vid_mode;         // Відеорежим консолі
    std::uint16_t root_dev;         // Застарілий номер кореневого пристрою
    std::uint16_t boot_flag;        // Сигнатура 0xAA55
    std::uint16_t jump;             // Інструкція короткого переходу (jmp)
    std::uint32_t header;           // Магічне число "HdrS"
    std::uint16_t version;          // Версія протоколу, 0x020f = 2.15
    std::uint32_t realmode_swtch;   // Вказівник на функцію перемикання режимів
    std::uint16_t start_sys_seg;    // Сегмент старту системи
    std::uint16_t kernel_version;   // Зсув рядка версії ядра в коді налаштування
    std::uint8_t  type_of_loader;   // Ідентифікатор завантажувача
    std::uint8_t  loadflags;        // Прапорці завантаження
    std::uint16_t setup_move_size;  // Розмір переміщення коду налаштування
    std::uint32_t code32_start;     // Точка входу в захищений режим (0x100000)
    std::uint32_t ramdisk_image;    // Фізична адреса initramfs у пам'яті
    std::uint32_t ramdisk_size;     // Розмір initramfs у байтах
    std::uint32_t bootsect_kludge;  // Застаріле
    std::uint16_t heap_end_ptr;     // Зсув кінця купи завантажувача
    std::uint8_t  ext_loader_ver;   // Розширений номер версії завантажувача
    std::uint8_t  ext_loader_type;  // Розширений тип завантажувача
    std::uint32_t cmd_line_ptr;     // Фізична адреса рядка параметрів ядра
    std::uint32_t initrd_addr_max;  // Найвища допустима адреса кінця initramfs
};

// Розкладка байтів — частина контракту з ядром, тож фіксуємо її перевіркою.
static_assert(sizeof(SetupHeader) == 63, "setup_header мусить бути щільним");

enum class Error {
    Open,          // файл не відкрився
    Read,          // збій позиціювання або читання
    Truncated,     // образ коротший за заголовок
    BadMagic,      // немає "HdrS"
    BadBootFlag,   // немає 0xAA55
    OldProtocol,   // протокол старіший за 2.02
    NoVersion,     // рядка версії ядра немає
    OutOfRange     // розміщення не влазить у дозволені межі
};

std::string_view describe(Error e) noexcept;

// Куди завантажувач кладе initramfs і рядок параметрів.
struct LoadPlan {
    std::uint32_t initrd_phys{};
    std::uint32_t initrd_size{};
    std::uint32_t cmdline_phys{};
};

class KernelImage {
public:
    // Відкриває bzImage і одразу перевіряє магічне число, сигнатуру й версію.
    static std::expected<KernelImage, Error> load(std::filesystem::path path);

    const SetupHeader& header() const noexcept { return header_; }

    std::size_t   setup_size() const noexcept;      // байтів коду налаштування
    std::uint64_t protected_size() const noexcept;  // байтів захищеного коду
    std::uint32_t initrd_addr_max() const noexcept;

    std::expected<std::string, Error> kernel_version() const;
    std::expected<void, Error>        fill_loader_fields(const LoadPlan& plan);

    std::string describe_header() const;

private:
    KernelImage(std::filesystem::path path, SetupHeader header)
        : path_{std::move(path)}, header_{header} {}

    std::filesystem::path path_;
    SetupHeader           header_{};
};

}  // namespace boot
