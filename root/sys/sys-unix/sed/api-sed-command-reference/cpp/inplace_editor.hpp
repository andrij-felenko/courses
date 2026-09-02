// inplace_editor.hpp — механіка sed -i: тіньова копія поруч із ціллю
// та атомарна підміна запису каталогу викликом rename(2).
#pragma once

#include <expected>
#include <filesystem>
#include <optional>
#include <string>
#include <string_view>
#include <system_error>

namespace minised {

class InPlaceEditor {
public:
    struct Options {
        std::optional<std::string> backup_suffix;  // -i.bak
        bool follow_symlinks{false};               // --follow-symlinks
    };

    // Помилка повертається як std::error_code: жодних -1 із errno назовні.
    static std::expected<void, std::error_code> commit(const std::filesystem::path& target,
                                                       std::string_view content,
                                                       const Options& opts);
};

}  // namespace minised
