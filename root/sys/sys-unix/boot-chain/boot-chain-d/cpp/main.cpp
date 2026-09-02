// bootchain header <vmlinuz> [initramfs]
// bootchain switch-root <новий-корінь> <init> [аргументи…]
#include "boot_header.hpp"
#include "switch_root.hpp"

#include <cstdint>
#include <cstdio>
#include <filesystem>
#include <print>
#include <span>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>

#include <unistd.h>

namespace {

void usage(std::string_view prog)
{
    std::println(stderr,
                 "Використання:\n"
                 "  {0} header <vmlinuz> [initramfs]\n"
                 "  {0} switch-root <новий-корінь> <init> [аргументи…]",
                 prog);
}

// Реальний завантажувач кладе initramfs якомога вище під стелю initrd_addr_max.
std::uint32_t plan_initrd_base(std::uint32_t addr_max, std::uintmax_t size)
{
    const std::uint64_t top = static_cast<std::uint64_t>(addr_max) + 1;
    if (size == 0 || size > top)
        return 0;
    return static_cast<std::uint32_t>((top - size) & ~static_cast<std::uint64_t>(0xFFF));
}

int cmd_header(const std::filesystem::path& kernel, const std::filesystem::path* initrd)
{
    auto image = boot::KernelImage::load(kernel);
    if (!image) {
        std::println(stderr, "{}: {}", kernel.string(), boot::describe(image.error()));
        return 1;
    }
    std::print("{}", image->describe_header());

    boot::LoadPlan plan{};
    if (initrd != nullptr) {
        std::error_code ec;
        const auto size = std::filesystem::file_size(*initrd, ec);
        if (ec) {
            std::println(stderr, "{}: {}", initrd->string(), ec.message());
            return 1;
        }
        plan.initrd_size = static_cast<std::uint32_t>(size);
        plan.initrd_phys = plan_initrd_base(image->initrd_addr_max(), size);
        if (plan.initrd_phys == 0) {
            std::println(stderr, "{}: образ не влазить під стелю initrd_addr_max",
                         initrd->string());
            return 1;
        }
        plan.cmdline_phys = plan.initrd_phys - 0x1000;
    } else {
        plan.cmdline_phys = 0x20000;
    }

    if (auto ok = image->fill_loader_fields(plan); !ok) {
        std::println(stderr, "заповнення полів завантажувача: {}", boot::describe(ok.error()));
        return 1;
    }

    std::println("\nПісля заповнення полів завантажувачем:");
    std::print("{}", image->describe_header());
    return 0;
}

int cmd_switch_root(std::span<char*> rest)
{
    if (rest.size() < 2) {
        std::println(stderr, "switch-root: потрібні новий корінь і шлях до init");
        return 2;
    }
    if (::geteuid() != 0) {
        std::println(stderr, "switch-root: потрібні права root");
        return 1;
    }
    if (::getpid() != 1)
        std::println(stderr, "switch-root: попередження — це не PID 1, "
                             "справжній перехід робить лише перший процес");

    const std::vector<std::string> args{rest.begin() + 2, rest.end()};
    const boot::SwitchRoot switcher{std::filesystem::path{rest[0]}};

    auto ok = switcher.run(std::filesystem::path{rest[1]}, args);
    // Сюди потрапляємо лише за невдачі: після успішного exec коду вже немає.
    std::println(stderr, "switch-root: {}", ok.error().message());
    return 1;
}

}  // namespace

int main(int argc, char** argv)
{
    const std::span<char*> args{argv, static_cast<std::size_t>(argc)};
    if (args.size() < 2) {
        usage(args[0]);
        return 2;
    }

    const std::string_view command{args[1]};
    if (command == "header") {
        if (args.size() < 3) {
            usage(args[0]);
            return 2;
        }
        const std::filesystem::path kernel{args[2]};
        if (args.size() > 3) {
            const std::filesystem::path initrd{args[3]};
            return cmd_header(kernel, &initrd);
        }
        return cmd_header(kernel, nullptr);
    }
    if (command == "switch-root")
        return cmd_switch_root(args.subspan(2));

    usage(args[0]);
    return 2;
}
