namespace std::contracts {

    // Класифікація контрактного специфікатора за його синтаксичною роллю
    enum class contract_kind : unsigned char {
        pre,        // Преумова функції (pre)
        post,       // Постумова функції (post)
        assert      // Внутрішнє твердження в тілі блоку (contract_assert)
    };

    // Спосіб ідентифікації та реєстрації порушення під час оцінки
    enum class detection_mode : unsigned char {
        predicate_false,      // Вираз предиката успішно обчислився і повернув false
        evaluation_exception  // Під час обчислення предиката виник необроблений виняток
    };

    // Клас метаданих порушення контракту
    class contract_violation {
    public:
        // Конструктори копіювання та переміщення видалені для збереження цілісності рантайму
        contract_violation(const contract_violation&) = delete;
        contract_violation(contract_violation&&) = delete;
        contract_violation& operator=(const contract_violation&) = delete;
        contract_violation& operator=(contract_violation&&) = delete;

        // Номер рядка вихідного коду, де оголошено відповідний контракт
        [[nodiscard]] constexpr uint_least32_t line_number() const noexcept;

        // Ім'я або повний шлях до файлу вихідного коду (UTF-8 рядок із нульовим байтом)
        [[nodiscard]] constexpr const char* file_name() const noexcept;

        // Сигнатура або ім'я функції, до якої прив'язано контракт
        [[nodiscard]] constexpr const char* function_name() const noexcept;

        // Текст або мітка контракту, зазначена в квадратних дужках [name]
        [[nodiscard]] constexpr const char* comment() const noexcept;

        // Текстовий запис виразу предиката мовою C++
        [[nodiscard]] constexpr const char* predicate() const noexcept;

        // Вид контракту: pre, post або assert
        [[nodiscard]] constexpr contract_kind kind() const noexcept;

        // Причина спрацювання механізму порушення
        [[nodiscard]] constexpr detection_mode detection_mode() const noexcept;
    };

} // namespace std::contracts
