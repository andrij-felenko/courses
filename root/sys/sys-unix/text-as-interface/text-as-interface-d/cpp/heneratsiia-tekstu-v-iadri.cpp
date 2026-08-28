#include <string>
#include <string_view>
#include <format>

// Безпечна генерація форматованого рядкового запису (C++20)
std::string format_mount_entry_cpp(int id, int parent_id,
                                   unsigned int major, unsigned int minor,
                                   std::string_view mountpoint,
                                   std::string_view root,
                                   std::string_view fstype) {
    return std::format("{} {} {}:{} {} {} {}\n",
                        id, parent_id, major, minor, mountpoint, root, fstype);
}
