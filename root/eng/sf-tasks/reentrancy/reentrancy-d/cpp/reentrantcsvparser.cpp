#include <iostream>
#include <string_view>
#include <cstddef>

// РЕЕНТЕРАБЕЛЬНИЙ ПАРСЕР (C++): об'єктний підхід із явним контекстом стану.
// Контекст зберігає стан всередині об'єкта, створеного на стекі викликача.
class ReentrantCsvParser {
public:
    struct Context {
        std::string_view remaining_data;
        char delimiter{','};
        std::size_t tokens_parsed{0};
    };

    static void init(Context& ctx, std::string_view input, char delimiter = ',') {
        ctx.remaining_data = input;
        ctx.delimiter = delimiter;
        ctx.tokens_parsed = 0;
    }

    static std::string_view next_token(Context& ctx) {
        if (ctx.remaining_data.empty()) {
            return {};
        }

        auto delim_pos = ctx.remaining_data.find(ctx.delimiter);
        std::string_view token;

        if (delim_pos == std::string_view::npos) {
            token = ctx.remaining_data;
            ctx.remaining_data = {};
        } else {
            token = ctx.remaining_data.substr(0, delim_pos);
            ctx.remaining_data.remove_prefix(delim_pos + 1);
        }

        ctx.tokens_parsed++;
        return token;
    }
};
