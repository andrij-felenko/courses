// notification_renderer.hpp & notification_renderer.cpp
// Високопродуктивна C++20 реалізація конвеєра рендерингу сповіщень

#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <variant>
#include <sstream>
#include <iomanip>
#include <cmath>

namespace notify {

enum class Channel { Email, Push, Sms, InApp };

struct RecipientContext {
    std::string userId;
    std::string locale;   // "uk-UA", "en-US"
    std::string timezone; // "Europe/Kyiv"
    std::vector<Channel> channels;
};

struct EventPayload {
    std::string orderId;
    std::string customerName;
    int64_t amountCents;
    std::string currency;
    int64_t itemsCount;
    std::string createdAtUtc;
};

// Вузли AST
struct LiteralNode { std::string value; };
struct VariableNode { std::string key; };
struct CurrencyNode { std::string key; std::string currencyKey; };
struct DateTimeNode { std::string key; };

struct ASTElement;
struct PluralNode {
    std::string key;
    std::unordered_map<std::string, std::vector<ASTElement>> variants;
};

struct ASTElement {
    std::variant<LiteralNode, VariableNode, CurrencyNode, DateTimeNode, PluralNode> node;
};

// Безпечне екранування тексту для HTML
class ContextEscaper {
public:
    static std::string escapeHtml(std::string_view input) {
        std::string out;
        out.reserve(input.size() + 16);
        for (char c : input) {
            switch (c) {
                case '&': out += "&amp;"; break;
                case '<': out += "&lt;"; break;
                case '>': out += "&gt;"; break;
                case '"': out += "&quot;"; break;
                case '\'': out += "&#039;"; break;
                default:  out += c; break;
            }
        }
        return out;
    }
};

// Обчислювач правил множини CLDR для української та англійської мов
class CldrPluralResolver {
public:
    static std::string resolve(std::string_view locale, int64_t count) {
        if (locale.starts_with("uk")) {
            int64_t mod10 = std::abs(count) % 10;
            int64_t mod100 = std::abs(count) % 100;
            if (mod10 == 1 && mod100 != 11) {
                return "one";
            }
            if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) {
                return "few";
            }
            if (mod10 == 0 || (mod10 >= 5 && mod10 <= 9) || (mod100 >= 11 && mod100 <= 14)) {
                return "many";
            }
            return "other";
        }
        // За замовчуванням англійське правило (one vs other)
        return (std::abs(count) == 1) ? "one" : "other";
    }
};

// Головний рушій рендерингу
class NotificationRenderer {
public:
    std::string evaluateAst(
        const std::vector<ASTElement>& nodes,
        const std::unordered_map<std::string, std::string>& payload,
        const RecipientContext& recipient,
        bool isHtml
    ) {
        std::string result;
        for (const auto& elem : nodes) {
            std::visit([&](const auto& n) {
                using T = std::decay_t<decltype(n)>;
                if constexpr (std::is_same_v<T, LiteralNode>) {
                    result += n.value;
                } else if constexpr (std::is_same_v<T, VariableNode>) {
                    auto it = payload.find(n.key);
                    std::string raw = (it != payload.end()) ? it->second : "";
                    result += isHtml ? ContextEscaper::escapeHtml(raw) : raw;
                } else if constexpr (std::is_same_v<T, CurrencyNode>) {
                    auto itVal = payload.find(n.key);
                    int64_t cents = (itVal != payload.end()) ? std::stoll(itVal->second) : 0;
                    double units = cents / 100.0;
                    std::ostringstream ss;
                    ss << std::fixed << std::setprecision(2) << units << " USD";
                    std::string formatted = ss.str();
                    result += isHtml ? ContextEscaper.escapeHtml(formatted) : formatted;
                } else if constexpr (std::is_same_v<T, DateTimeNode>) {
                    auto it = payload.find(n.key);
                    std::string raw = (it != payload.end()) ? it->second : "";
                    result += isHtml ? ContextEscaper.escapeHtml(raw) : raw;
                } else if constexpr (std::is_same_v<T, PluralNode>) {
                    auto it = payload.find(n.key);
                    int64_t count = (it != payload.end()) ? std::stoll(it->second) : 0;
                    std::string cat = CldrPluralResolver::resolve(recipient.locale, count);
                    
                    auto branchIt = n.variants.find(cat);
                    if (branchIt == n.variants.end()) {
                        branchIt = n.variants.find("other");
                    }
                    if (branchIt != n.variants.end()) {
                        auto subPayload = payload;
                        subPayload["#"] = std::to_string(count);
                        result += evaluateAst(branchIt->second, subPayload, recipient, isHtml);
                    }
                }
            }, elem.node);
        }
        return result;
    }
};

} // namespace notify
