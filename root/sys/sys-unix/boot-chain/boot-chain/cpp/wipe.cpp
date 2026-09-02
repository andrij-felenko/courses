#include "wipe.hpp"

#include <cerrno>
#include <memory>
#include <string>
#include <string_view>
#include <vector>

#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>

namespace {

// Знімок імен каталогу. Читаємо все наперед і лише потім видаляємо: міняти
// каталог просто під readdir — найкоротший шлях до пропущених записів.
std::vector<std::string> snapshot(int dir_fd, std::size_t& errors)
{
    std::vector<std::string> names;

    // fdopendir забирає дескриптор собі, а dir_fd потрібен нам і після
    // обходу — тому віддаємо копію, і одразу під RAII: гілок виходу нижче
    // достатньо, щоб ручний close колись загубився.
    boot::UniqueFd copy(::dup(dir_fd));
    if (!copy) {
        const int err = errno;
        boot::warn("dup", err);
        ++errors;
        return names;
    }

    DIR* const raw = ::fdopendir(copy.get());
    if (raw == nullptr) {
        const int err = errno;
        boot::warn("fdopendir", err);
        ++errors;
        return names;
    }
    copy.release();  // тепер дескриптором володіє DIR*, його закриє closedir

    const std::unique_ptr<DIR, decltype(&::closedir)> dir(raw, &::closedir);
    while (const dirent* const entry = ::readdir(dir.get())) {
        const std::string_view name(entry->d_name);
        if (name == "." || name == "..")
            continue;
        names.emplace_back(name);
    }
    return names;
}

// Стирає вміст каталогу dir_fd, не сходячи з пристрою dev.
// Дескриптор лишається за викликачем — закривати його тут не можна.
std::size_t wipe_contents(int dir_fd, dev_t dev)
{
    std::size_t errors = 0;
    const std::vector<std::string> names = snapshot(dir_fd, errors);

    for (const std::string& name : names) {
        struct ::stat st {};
        if (::fstatat(dir_fd, name.c_str(), &st, AT_SYMLINK_NOFOLLOW) != 0) {
            const int err = errno;
            boot::warn("fstatat " + name, err);
            ++errors;
            continue;
        }

        if (!S_ISDIR(st.st_mode)) {
            // Звичайний файл, симвлінк, сокет, пристрій — просто відв'язуємо:
            // вміст ramfs зникає разом з останнім посиланням на нього.
            if (::unlinkat(dir_fd, name.c_str(), 0) != 0) {
                const int err = errno;
                boot::warn("unlinkat " + name, err);
                ++errors;
            }
            continue;
        }

        // Інший пристрій означає точку монтування: там уже не наша пам'ять.
        // Саме ця перевірка рятує щойно змонтований /sysroot.
        if (st.st_dev != dev)
            continue;

        boot::UniqueFd sub = boot::open_dir(dir_fd, name.c_str());
        if (!sub) {
            const int err = errno;
            boot::warn("openat " + name, err);
            ++errors;
            continue;
        }
        errors += wipe_contents(sub.get(), dev);
        sub.reset();  // глибше він уже не потрібен

        // Каталог знімається лише після того, як спорожнів: непорожній дасть
        // ENOTEMPTY, і про це варто сказати вголос.
        if (::unlinkat(dir_fd, name.c_str(), AT_REMOVEDIR) != 0) {
            const int err = errno;
            boot::warn("rmdir " + name, err);
            ++errors;
        }
    }
    return errors;
}

}  // namespace

namespace boot::wipe {

std::size_t filesystem(const UniqueFd& root)
{
    struct ::stat st {};
    if (::fstat(root.get(), &st) != 0) {
        const int err = errno;
        warn("fstat /", err);
        return 1;
    }
    // Знищення метаданих ramfs миттєво повертає сторінки в Buddy Allocator:
    // там немає ні кешу сторінок, ні відкладеного запису — лише самі дані.
    return wipe_contents(root.get(), st.st_dev);
}

}  // namespace boot::wipe
