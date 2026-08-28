namespace std::contracts {
    enum class detection_mode {
        predicate_false,
        evaluation_exception
    };

    class contract_violation {
    public:
        uint_least32_t line_number() const noexcept;
        string_view file_name() const noexcept;
        string_view function_name() const noexcept;
        string_view comment() const noexcept;
        string_view predicate() const noexcept;
        detection_mode mode() const noexcept;
    };
}
