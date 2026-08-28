#include <iostream>
#include <string_view>
#include <expected>
#include <system_error>
#include <format>
#include <sys/mount.h>

/* Ідіоматична обгортка mount(2) на C++23 */
enum class MountError {
    PermissionDenied,
    DeviceBusy,
    InvalidSuperblock,
    UnknownFilesystem,
    TargetNotFound,
    SystemFailure
};

[[nodiscard]] std::expected<void, std::pair<MountError, std::string>>
mountFilesystem(std::string_view source, std::string_view target, std::string_view fstype) {
    constexpr unsigned long flags = MS_RDONLY | MS_NODEV | MS_NOSUID | MS_NOEXEC;
    constexpr std::string_view dataOpts = "errors=remount-ro,data=ordered";

    if (::mount(source.data(), target.data(), fstype.data(), flags, dataOpts.data()) < 0) {
        const int err = errno;
        MountError category = MountError::SystemFailure;

        switch (err) {
            case EPERM:
            case EACCES: category = MountError::PermissionDenied; break;
            case EBUSY:  category = MountError::DeviceBusy; break;
            case EINVAL: category = MountError::InvalidSuperblock; break;
            case ENODEV: category = MountError::UnknownFilesystem; break;
            case ENOENT: category = MountError::TargetNotFound; break;
            default:     category = MountError::SystemFailure; break;
        }

        return std::unexpected(std::make_pair(
            category,
            std::format("Збій монтування '{}' на '{}': {} (errno={})",
                        source, target, std::generic_category().message(err), err)
        ));
    }
    return {};
}
