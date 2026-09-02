#include "mount_ops.hpp"

#include "posix.hpp"

#include <array>
#include <cerrno>
#include <string_view>

#include <sys/mount.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

namespace {

// Не вдалося перенести — відчіплюємо, інакше монтування триматиме стару
// rootfs у пам'яті і стирання не поверне сторінок ядру. MNT_DETACH відчіплює
// гілку негайно, а звільняє тоді, коли останній користувач закриє дескриптор.
void detach(const fs::path& path)
{
    if (::umount2(path.c_str(), MNT_DETACH) != 0) {
        const int err = errno;
        boot::warn("umount2 MNT_DETACH " + path.string(), err);
    }
}

}  // namespace

namespace boot::mounts {

bool is_mount_point(const fs::path& path)
{
    struct ::stat self {};
    struct ::stat parent {};

    if (::lstat(path.c_str(), &self) != 0 || !S_ISDIR(self.st_mode))
        return false;
    if (::stat((path / "..").c_str(), &parent) != 0)
        return false;

    return self.st_dev != parent.st_dev;
}

void make_tree_private()
{
    // MS_MOVE відмовляє з EINVAL на монтуванні зі спільним поширенням:
    // ядро не знає, куди транслювати переміщення для решти простору імен.
    // Сучасний initramfs успадковує саме shared, тож знімаємо це з дерева.
    checked(::mount(nullptr, "/", nullptr, MS_REC | MS_PRIVATE, nullptr),
            "mount / MS_REC|MS_PRIVATE");
}

std::size_t move_special(const fs::path& new_root)
{
    // Ці дерева тримають відкриті дескриптори й активні структури ядра
    // (udev, сокети, консоль), тому їх не демонтують, а переставляють цілими.
    static constexpr std::array<std::string_view, 4> kept{"/dev", "/proc",
                                                          "/sys", "/run"};

    std::size_t failed = 0;
    for (const std::string_view name : kept) {
        const fs::path src(name);
        if (!is_mount_point(src))
            continue;  // у мінімальному initramfs його могло й не бути

        // relative_path() зрізає провідний '/', інакше operator/ просто
        // відкинув би new_root і лишив абсолютний шлях старого кореня.
        const fs::path dst = new_root / src.relative_path();

        std::error_code ec;
        if (!fs::is_directory(dst, ec)) {
            // MS_MOVE вимагає готового каталогу-цілі. Створювати його не
            // будемо: відсутність означає, що змонтовано щось не те.
            warn("у новому корені немає " + dst.string() + " — відчіплюю "
                 + src.string());
            detach(src);
            ++failed;
            continue;
        }

        // MS_MOVE переносить гілку цілком, разом з усім, що змонтоване під
        // нею (/dev/pts, /dev/shm), і не чіпає відкритих файлів.
        if (::mount(src.c_str(), dst.c_str(), nullptr, MS_MOVE, nullptr) != 0) {
            const int err = errno;
            warn("MS_MOVE " + src.string() + " -> " + dst.string(), err);
            detach(src);
            ++failed;
        }
    }
    return failed;
}

}  // namespace boot::mounts
