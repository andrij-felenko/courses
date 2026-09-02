// Текстові метадані LUKS2: розбір документа й перевірка інваріантів —
// схеми словників, перехресних посилань і перекриття дискових областей.
#pragma once

#include <cstdint>
#include <expected>
#include <iosfwd>
#include <string>
#include <string_view>
#include <vector>

#include <nlohmann/json.hpp>

#include "header.hpp"

namespace luks2 {

struct Finding {
    enum class Level { error, warning };

    Level level;
    std::string text;

    bool is_error() const noexcept { return level == Level::error; }
};

class Metadata {
public:
    static std::expected<Metadata, Error> parse(std::string_view text);

    // Друкує граф об'єктів: шпарини, токени, сегменти, дайджести.
    void print(std::ostream& out) const;

    // Порушення в порядку виявлення; помилка означає, що ядро віддасть -EINVAL.
    std::vector<Finding> validate(std::uint64_t hdr_size) const;

private:
    explicit Metadata(nlohmann::json document) noexcept
        : document_{std::move(document)} {}

    nlohmann::json document_;
};

}  // namespace luks2
