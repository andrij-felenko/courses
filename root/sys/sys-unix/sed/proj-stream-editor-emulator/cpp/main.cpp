#include <iostream>
#include <string>
#include <vector>
#include <regex>
#include <memory>
#include <optional>

enum class CommandType {
    Subst,
    Print,
    Delete,
    HoldCopy,
    HoldAppend,
    GetCopy,
    GetAppend,
    Exchange,
    NextAppend
};

struct SedCommand {
    CommandType type;
    int line_addr{0};
    std::optional<std::regex> regex_addr;
    std::string subst_pattern;
    std::string subst_replacement;
    bool subst_global{false};
};

class SedEngine {
public:
    explicit SedEngine(bool quiet = false) : quiet_mode_(quiet) {}

    void process_stream(std::istream& in, const std::vector<SedCommand>& commands) {
        std::string raw_line;
        while (std::getline(in, raw_line)) {
            line_number_++;
            deleted_ = false;
            pattern_space_ = raw_line;

            for (const auto& cmd : commands) {
                execute_command(cmd, in);
                if (deleted_) {
                    break;
                }
            }

            if (!deleted_ && !quiet_mode_) {
                std::cout << pattern_space_ << '\n';
            }
        }
    }

private:
    void execute_command(const SedCommand& cmd, std::istream& in) {
        if (cmd.line_addr > 0 && static_cast<size_t>(cmd.line_addr) != line_number_) {
            return;
        }
        if (cmd.regex_addr.has_value()) {
            if (!std::regex_search(pattern_space_, *cmd.regex_addr)) {
                return;
            }
        }

        switch (cmd.type) {
            case CommandType::Subst: {
                std::regex re(cmd.subst_pattern);
                auto flags = cmd.subst_global 
                    ? std::regex_constants::match_default 
                    : std::regex_constants::format_first_only;
                pattern_space_ = std::regex_replace(pattern_space_, re, cmd.subst_replacement, flags);
                break;
            }
            case CommandType::Print:
                std::cout << pattern_space_ << '\n';
                break;
            case CommandType::Delete:
                deleted_ = true;
                break;
            case CommandType::HoldCopy:
                hold_space_ = pattern_space_;
                break;
            case CommandType::HoldAppend:
                if (!hold_space_.empty()) {
                    hold_space_ += '\n';
                }
                hold_space_ += pattern_space_;
                break;
            case CommandType::GetCopy:
                pattern_space_ = hold_space_;
                break;
            case CommandType::GetAppend:
                if (!pattern_space_.empty()) {
                    pattern_space_ += '\n';
                }
                pattern_space_ += hold_space_;
                break;
            case CommandType::Exchange:
                std::swap(pattern_space_, hold_space_);
                break;
            case CommandType::NextAppend: {
                std::string next_line;
                if (std::getline(in, next_line)) {
                    line_number_++;
                    pattern_space_ += '\n' + next_line;
                }
                break;
            }
        }
    }

    std::string pattern_space_;
    std::string hold_space_;
    size_t line_number_{0};
    bool quiet_mode_{false};
    bool deleted_{false};
};

int main() {
    SedEngine engine(false);

    std::vector<SedCommand> cmds;
    cmds.push_back(SedCommand{
        .type = CommandType::Subst,
        .line_addr = 0,
        .regex_addr = std::nullopt,
        .subst_pattern = "WARN",
        .subst_replacement = "ALERT",
        .subst_global = true
    });

    engine.process_stream(std::cin, cmds);
    return 0;
}
