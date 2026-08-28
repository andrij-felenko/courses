#include <cstdint>
#include <sys/types.h>
#include <sys/stat.h>
#include <cerrno>

// Ідіоматична C++ реалізація алгоритму перевірки прав VFS
enum class AccessMode : uint32_t {
    Read = 4,
    Write = 2,
    Execute = 1
};

[[nodiscard]] constexpr int check_dac_permission(
    uid_t current_fsuid, gid_t current_fsgid,
    uid_t inode_uid, gid_t inode_gid,
    mode_t inode_mode, AccessMode requested) noexcept
{
    const auto req = static_cast<uint32_t>(requested);

    // 1. Перевірка прав власника
    if (current_fsuid == inode_uid) {
        return ((inode_mode >> 6) & req) == req ? 0 : -EACCES;
    }

    // 2. Перевірка прав групи
    if (current_fsgid == inode_gid) {
        return ((inode_mode >> 3) & req) == req ? 0 : -EACCES;
    }

    // 3. Перевірка прав сторонніх користувачів
    return (inode_mode & req) == req ? 0 : -EACCES;
}
