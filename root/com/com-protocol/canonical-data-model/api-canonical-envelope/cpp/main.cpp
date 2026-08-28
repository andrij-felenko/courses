#include <string>
#include <string_view>
#include <expected>
#include <vector>
#include <cstdint>

enum class TranslationErrorCode {
    MalformedSourceSyntax,     // Помилка парсингу (битий JSON/XML/Protobuf)
    MissingRequiredField,      // Відсутній обов'язковий атрибут джерела
    SemanticTypeMismatch,      // Неможливо перетворити рядок у число/дату
    UnknownEnumerationValue,   // Статус або код не підтримується словником
    SchemaViolation,           // Порушення інваріантів схеми
    ValidationConstraintFailed // Бізнес-помилка (наприклад, від'ємна сума)
};

struct TranslationError {
    TranslationErrorCode code;
    std::string field_path;
    std::string message;
    std::string raw_value;
};

template <typename TSource, typename TTarget>
class ICanonicalTranslator {
public:
    virtual ~ICanonicalTranslator() = default;

    // Пряма трансляція: Джерело -> Канонічна модель
    virtual std::expected<TTarget, TranslationError>
    translate(const TSource& source, std::string_view correlation_id) = 0;
};
