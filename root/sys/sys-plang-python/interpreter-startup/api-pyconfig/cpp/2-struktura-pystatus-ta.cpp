/* С++ еквівалент для перевірки стану ініціалізації CPython */
namespace py {

struct Status {
    enum class Type {
        Ok = 0,
        Error = 1,
        Exit = 2
    };

    Type type{Type::Ok};
    std::string function_name{};
    std::string error_message{};
    int exit_code{0};

    [[nodiscard]] bool is_ok() const noexcept { return type == Type::Ok; }
    [[nodiscard]] bool is_error() const noexcept { return type == Type::Error; }
    [[nodiscard]] bool is_exit() const noexcept { return type == Type::Exit; }
};

} // namespace py
