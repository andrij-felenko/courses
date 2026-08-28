#include <iostream>
#include <string_view>
#include <span>
#include <vector>
#include <memory>
#include <variant>
#include <optional>
#include <cstdint>
#include <cstring>

namespace messaging {

enum class ValueType {
    String,
    Int64,
    Double,
    Bitmask
};

/* Типізоване значення заголовка з підтримкою string_view (нульове копіювання) */
using HeaderValue = std::variant<std::string_view, int64_t, double, uint64_t>;

struct MessageHeader {
    std::string_view key;
    HeaderValue value;
};

/* Незмінне повідомлення з легкою структурою метаданих */
class Message {
public:
    Message(uint64_t id, std::span<const uint8_t> payload)
        : id_(id), payload_(payload) {}

    void add_header(std::string_view key, HeaderValue value) {
        headers_.push_back({key, std::move(value)});
    }

    [[nodiscard]] uint64_t id() const noexcept { return id_; }
    [[nodiscard]] std::span<const uint8_t> payload() const noexcept { return payload_; }
    [[nodiscard]] const std::vector<MessageHeader>& headers() const noexcept { return headers_; }

    [[nodiscard]] std::optional<HeaderValue> find_header(std::string_view key) const noexcept {
        for (const auto& [k, v] : headers_) {
            if (k == key) return v;
        }
        return std::nullopt;
    }

private:
    uint64_t id_;
    std::span<const uint8_t> payload_;
    std::vector<MessageHeader> headers_;
};

enum class FilterDecision {
    Pass,
    Drop,
    DeadLetter
};

enum class ErrorPolicy {
    DropOnError,
    PassOnError,
    DeadLetterOnError
};

/* Базовий інтерфейс окремого предикату */
class IPredicate {
public:
    virtual ~IPredicate() = default;
    [[nodiscard]] virtual std::optional<bool> evaluate(const Message& msg) const noexcept = 0;
};

/* Предикат суворої рядкової рівності */
class StringEqualsPredicate final : public IPredicate {
public:
    StringEqualsPredicate(std::string_view header_key, std::string_view expected_value, bool invert = false)
        : key_(header_key), expected_(expected_value), invert_(invert) {}

    [[nodiscard]] std::optional<bool> evaluate(const Message& msg) const noexcept override {
        auto val = msg.find_header(key_);
        if (!val.has_value()) return std::nullopt; // Заголовок відсутній

        if (const auto* str_ptr = std::get_if<std::string_view>(&*val)) {
            bool matches = (*str_ptr == expected_);
            return matches ^ invert_;
        }
        return std::nullopt; // Невідповідність типу
    }

private:
    std::string_view key_;
    std::string_view expected_;
    bool invert_;
};

/* Предикат порівняння цілих чисел (Greater Than) */
class IntGreaterThanPredicate final : public IPredicate {
public:
    IntGreaterThanPredicate(std::string_view header_key, int64_t threshold)
        : key_(header_key), threshold_(threshold) {}

    [[nodiscard]] std::optional<bool> evaluate(const Message& msg) const noexcept override {
        auto val = msg.find_header(key_);
        if (!val.has_value()) return std::nullopt;

        if (const auto* i_ptr = std::get_if<int64_t>(&*val)) {
            return (*i_ptr > threshold_);
        }
        return std::nullopt;
    }

private:
    std::string_view key_;
    int64_t threshold_;
};

/* Композитний логічний оператор AND над списком підпредикатів */
class AndCompositePredicate final : public IPredicate {
public:
    void add(std::unique_ptr<IPredicate> pred) {
        children_.push_back(std::move(pred));
    }

    [[nodiscard]] std::optional<bool> evaluate(const Message& msg) const noexcept override {
        for (const auto& child : children_) {
            auto res = child->evaluate(msg);
            if (!res.has_value()) return std::nullopt; // Помилка обчислення
            if (!*res) return false; // Short-circuit: один false зупиняє весь AND
        }
        return true;
    }

private:
    std::vector<std::unique_ptr<IPredicate>> children_;
};

/* Метрики продуктивності конвеєра */
struct PipelineMetrics {
    uint64_t total_evaluated{0};
    uint64_t passed{0};
    uint64_t dropped{0};
    uint64_t dead_lettered{0};
};

/* Конвеєр фільтрації з обробкою помилок та збором статистики */
class FilterPipeline {
public:
    explicit FilterPipeline(ErrorPolicy policy = ErrorPolicy::DropOnError)
        : policy_(policy) {}

    void add_stage(std::unique_ptr<IPredicate> predicate) {
        stages_.push_back(std::move(predicate));
    }

    FilterDecision process(const Message& msg) noexcept {
        ++metrics_.total_evaluated;

        for (const auto& stage : stages_) {
            auto result = stage->evaluate(msg);

            if (!result.has_value()) {
                switch (policy_) {
                    case ErrorPolicy::DropOnError:
                        ++metrics_.dropped;
                        return FilterDecision::Drop;
                    case ErrorPolicy::PassOnError:
                        continue;
                    case ErrorPolicy::DeadLetterOnError:
                        ++metrics_.dead_lettered;
                        return FilterDecision::DeadLetter;
                }
            }

            if (!*result) {
                ++metrics_.dropped;
                return FilterDecision::Drop;
            }
        }

        ++metrics_.passed;
        return FilterDecision::Pass;
    }

    [[nodiscard]] const PipelineMetrics& metrics() const noexcept { return metrics_; }

private:
    ErrorPolicy policy_;
    std::vector<std::unique_ptr<IPredicate>> stages_;
    PipelineMetrics metrics_;
};

} // namespace messaging

int main() {
    using namespace messaging;

    FilterPipeline pipeline(ErrorPolicy::DropOnError);

    // Додаємо стадію 1: region == "EU"
    pipeline.add_stage(std::make_unique<StringEqualsPredicate>("region", "EU"));

    // Додаємо стадію 2: priority > 3
    pipeline.add_stage(std::make_unique<IntGreaterThanPredicate>("priority", 3));

    // Створюємо тестове повідомлення № 1
    const std::string body1 = "{\"order_id\": 991, \"amount\": 450.00}";
    std::span<const uint8_t> span1(reinterpret_cast<const uint8_t*>(body1.data()), body1.size());
    Message msg1(1001, span1);
    msg1.add_header("region", std::string_view("EU"));
    msg1.add_header("priority", int64_t{5});

    // Створюємо тестове повідомлення № 2 (нецільовий регіон US)
    const std::string body2 = "{\"order_id\": 992, \"amount\": 120.00}";
    std::span<const uint8_t> span2(reinterpret_cast<const uint8_t*>(body2.data()), body2.size());
    Message msg2(1002, span2);
    msg2.add_header("region", std::string_view("US"));
    msg2.add_header("priority", int64_t{9});

    auto d1 = pipeline.process(msg1);
    auto d2 = pipeline.process(msg2);

    std::cout << "Повідомлення #1001 результат: " << (d1 == FilterDecision::Pass ? "PASS" : "DROP") << '\n';
    std::cout << "Повідомлення #1002 результат: " << (d2 == FilterDecision::Pass ? "PASS" : "DROP") << '\n';
    std::cout << "Метрики конвеєра: всього=" << pipeline.metrics().total_evaluated
              << ", пропущено=" << pipeline.metrics().passed
              << ", відсіяно=" << pipeline.metrics().dropped << '\n';

    return 0;
}
