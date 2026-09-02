#include "boot_header.hpp"

#include <format>
#include <fstream>
#include <utility>

namespace boot {
namespace {

std::expected<std::ifstream, Error> open_binary(const std::filesystem::path& path)
{
    std::ifstream in{path, std::ios::binary};
    if (!in)
        return std::unexpected{Error::Open};
    return in;
}

}  // namespace

std::string_view describe(Error e) noexcept
{
    switch (e) {
    case Error::Open:        return "не вдалося відкрити образ";
    case Error::Read:        return "збій читання образу";
    case Error::Truncated:   return "образ коротший за setup_header";
    case Error::BadMagic:    return "немає магічного числа \"HdrS\": це не bzImage";
    case Error::BadBootFlag: return "немає сигнатури 0xAA55";
    case Error::OldProtocol: return "протокол завантаження старіший за 2.02";
    case Error::NoVersion:   return "в образі немає рядка версії ядра";
    case Error::OutOfRange:  return "розміщення не влазить у дозволені межі";
    }
    return "невідома помилка";
}

std::expected<KernelImage, Error> KernelImage::load(std::filesystem::path path)
{
    auto in = open_binary(path);
    if (!in)
        return std::unexpected{in.error()};

    in->seekg(kHeaderOffset);
    if (!*in)
        return std::unexpected{Error::Read};

    SetupHeader header{};
    in->read(reinterpret_cast<char*>(&header), sizeof header);
    if (in->gcount() != static_cast<std::streamsize>(sizeof header))
        return std::unexpected{Error::Truncated};

    // Три перевірки, які завантажувач мусить зробити до стрибка в ядро.
    if (header.header != kHeaderMagic)
        return std::unexpected{Error::BadMagic};
    if (header.boot_flag != kBootFlag)
        return std::unexpected{Error::BadBootFlag};
    if (header.version < kProtoMin)
        return std::unexpected{Error::OldProtocol};

    return KernelImage{std::move(path), header};
}

std::size_t KernelImage::setup_size() const noexcept
{
    // Нуль у setup_sects історично означає чотири сектори.
    const unsigned sects = header_.setup_sects != 0 ? header_.setup_sects : 4u;
    return (static_cast<std::size_t>(sects) + 1) * 512;
}

std::uint64_t KernelImage::protected_size() const noexcept
{
    return static_cast<std::uint64_t>(header_.syssize) * 16;
}

std::uint32_t KernelImage::initrd_addr_max() const noexcept
{
    if (header_.version >= kProtoAddrMax && header_.initrd_addr_max != 0)
        return header_.initrd_addr_max;
    return kInitrdAddrMaxDefault;
}

std::expected<std::string, Error> KernelImage::kernel_version() const
{
    if (header_.kernel_version == 0)
        return std::unexpected{Error::NoVersion};

    // Поле зберігає зсув, зменшений на 0x200: у файлі шукаємо на 0x200 далі.
    const auto offset = static_cast<std::streamoff>(header_.kernel_version) + 0x200;
    if (std::cmp_greater_equal(offset, setup_size()))
        return std::unexpected{Error::OutOfRange};

    auto in = open_binary(path_);
    if (!in)
        return std::unexpected{in.error()};

    in->seekg(offset);
    if (!*in)
        return std::unexpected{Error::Read};

    std::string version;
    for (char c{}; in->get(c) && c != '\0';) {
        if (c < 0x20 || c > 0x7E)  // за межами друкованого ASCII — це вже не рядок
            break;
        version.push_back(c);
    }
    if (version.empty())
        return std::unexpected{Error::NoVersion};
    return version;
}

std::expected<void, Error> KernelImage::fill_loader_fields(const LoadPlan& plan)
{
    if (header_.version < kProtoMin)
        return std::unexpected{Error::OldProtocol};

    if (plan.initrd_size != 0) {
        if (plan.initrd_phys == 0)
            return std::unexpected{Error::OutOfRange};
        const std::uint64_t end =
            static_cast<std::uint64_t>(plan.initrd_phys) + plan.initrd_size - 1;
        if (end > initrd_addr_max())
            return std::unexpected{Error::OutOfRange};  // ядро туди не дотягнеться
    } else if (plan.initrd_phys != 0) {
        return std::unexpected{Error::OutOfRange};      // адреса без розміру
    }

    if (plan.cmdline_phys == 0)
        return std::unexpected{Error::OutOfRange};

    header_.type_of_loader = kLoaderUnknown;
    header_.loadflags |= kLoadedHigh;                   // ядро лежить за 0x100000
    header_.loadflags &= static_cast<std::uint8_t>(~kQuietFlag);
    header_.ramdisk_image = plan.initrd_phys;
    header_.ramdisk_size  = plan.initrd_size;
    header_.cmd_line_ptr  = plan.cmdline_phys;

    if (header_.loadflags & kCanUseHeap)
        header_.heap_end_ptr = static_cast<std::uint16_t>(0xE000 - 0x200);

    return {};
}

std::string KernelImage::describe_header() const
{
    std::string out = std::format("Образ: {}\n", path_.string());

    if (auto version = kernel_version(); version)
        out += std::format("  версія ядра           : {}\n", *version);

    out += std::format("  протокол завантаження : {}.{:02}\n",
                       header_.version >> 8, header_.version & 0xFF);
    out += std::format("  код налаштування      : {} байтів (setup_sects={})\n",
                       setup_size(), header_.setup_sects);
    out += std::format("  захищений код         : {} байтів\n", protected_size());
    out += std::format("  точка входу 32-біт    : {:#010x}\n", header_.code32_start);
    out += std::format("  стеля для initramfs   : {:#010x}\n", initrd_addr_max());
    out += std::format("  корінь read-only      : {}\n",
                       (header_.root_flags & 1u) ? "так" : "ні");
    out += std::format("  loadflags             : {:#04x}{}{}\n", header_.loadflags,
                       (header_.loadflags & kLoadedHigh) ? " LOADED_HIGH" : "",
                       (header_.loadflags & kCanUseHeap) ? " CAN_USE_HEAP" : "");
    out += std::format("  ramdisk_image/size    : {:#010x} / {}\n",
                       header_.ramdisk_image, header_.ramdisk_size);
    out += std::format("  cmd_line_ptr          : {:#010x}\n", header_.cmd_line_ptr);
    out += std::format("  type_of_loader        : {:#04x}\n", header_.type_of_loader);
    return out;
}

}  // namespace boot
