namespace std {
    class error_code {
    public:
        error_code() noexcept;
        error_code(int val, const error_category& cat) noexcept;

        template<class ErrorCodeEnum>
        error_code(ErrorCodeEnum e) noexcept;

        void assign(int val, const error_category& cat) noexcept;
        void clear() noexcept;

        int value() const noexcept;
        const error_category& category() const noexcept;
        error_condition default_error_condition() const noexcept;
        string message() const;

        explicit operator bool() const noexcept;
    };
}
