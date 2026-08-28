namespace std {
    class runtime_error : public exception {
    public:
        explicit runtime_error(const string& what_arg);
        explicit runtime_error(const char* what_arg);
        runtime_error(const runtime_error& other) noexcept;
        runtime_error& operator=(const runtime_error& other) noexcept;
        virtual ~runtime_error() noexcept;
    };
}
