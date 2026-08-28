#include <cstdint>
#include <string>
#include <string_view>
#include <system_error>

enum class DiophErrorCode {
    Ok = 0,
    OutOfMemory,
    InvalidArgument,
    VariableNotFound,
    DegreeOverflow,
    BufferTooSmall,
    EvaluationOverflow,
    ParseSyntaxError
};

struct DiophErrorCategory : std::error_category {
    [[nodiscard]] const char* name() const noexcept override {
        return "DiophBuilder";
    }
    [[nodiscard]] std::string message(int ev) const override {
        switch (static_cast<DiophErrorCode>(ev)) {
            case DiophErrorCode::Ok: return "Успішно";
            case DiophErrorCode::OutOfMemory: return "Вичерпано арену пам'яті";
            case DiophErrorCode::InvalidArgument: return "Некоректний аргумент функції";
            case DiophErrorCode::VariableNotFound: return "Змінну не знайдено в контексті";
            case DiophErrorCode::DegreeOverflow: return "Перевищено максимальний степінь многочлена";
            case DiophErrorCode::BufferTooSmall: return "Розмір вихідного буфера недостатній";
            case DiophErrorCode::EvaluationOverflow: return "Арифметичне переповнення під час обчислення";
            case DiophErrorCode::ParseSyntaxError: return "Синтаксична помилка при парсингу виразу";
            default: return "Невідома помилка";
        }
    }
};

inline const DiophErrorCategory& dioph_category() noexcept {
    static DiophErrorCategory category;
    return category;
}

inline std::error_code make_error_code(DiophErrorCode e) noexcept {
    return {static_cast<int>(e), dioph_category()};
}
