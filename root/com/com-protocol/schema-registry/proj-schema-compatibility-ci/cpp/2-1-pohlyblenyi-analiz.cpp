#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <optional>
#include <expected>

namespace schema_validator {

enum class DataType {
    Int32,
    Int64,
    String,
    Boolean
};

struct Field {
    std::string name;
    DataType type;
    bool has_default{false};
    std::optional<std::string> default_value{std::nullopt};
};

struct RecordSchema {
    std::string record_name;
    std::vector<Field> fields;

    [[nodiscard]] const Field* find_field(std::string_view name) const noexcept {
        for (const auto& field : fields) {
            if (field.name == name) return &field;
        }
        return nullptr;
    }
};

class SchemaCompatibilityEngine {
public:
    [[nodiscard]] static bool is_type_widening_allowed(DataType writer_type, DataType reader_type) noexcept {
        if (writer_type == reader_type) return true;
        // 32-бітне ціле число безпечно розширюється до 64-бітного
        if (writer_type == DataType::Int32 && reader_type == DataType::Int64) return true;
        return false;
    }

    /* Перевірка BACKWARD: Reader(new) може прочитати дані Writer(old) */
    [[nodiscard]] static std::expected<void, std::string> check_backward(
        const RecordSchema& old_writer,
        const RecordSchema& new_reader) {

        for (const auto& r_field : new_reader.fields) {
            const auto* w_field = old_writer.find_field(r_field.name);
            if (!w_field) {
                // Нове поле обов'язково повинно мати значення за замовчуванням
                if (!r_field.has_default) {
                    return std::unexpected(
                        "Помилка сумісності BACKWARD: Нове поле '" + r_field.name +
                        "' відсутнє у старій схемі та не має значення за замовчуванням."
                    );
                }
            } else {
                // Перевірка сумісності типу даних
                if (!is_type_widening_allowed(w_field->type, r_field->type)) {
                    return std::unexpected(
                        "Помилка сумісності BACKWARD: Поле '" + r_field.name +
                        "' має несумісну зміну типу даних."
                    );
                }
            }
        }
        return {};
    }

    /* Перевірка FORWARD: Reader(old) може прочитати дані Writer(new) */
    [[nodiscard]] static std::expected<void, std::string> check_forward(
        const RecordSchema& old_reader,
        const RecordSchema& new_writer) {
        // Пряма сумісність еквівалентна зворотній з обміном ролей читача й писаря
        return check_backward(new_writer, old_reader);
    }

    /* Перевірка FULL: Двостороння сумісність */
    [[nodiscard]] static std::expected<void, std::string> check_full(
        const RecordSchema& old_schema,
        const RecordSchema& new_schema) {

        if (auto res = check_backward(old_schema, new_schema); !res) {
            return res;
        }
        return check_forward(old_schema, new_schema);
    }
};

} // namespace schema_validator
