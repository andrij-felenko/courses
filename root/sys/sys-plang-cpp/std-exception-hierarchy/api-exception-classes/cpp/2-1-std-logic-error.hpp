namespace std {
    class logic_error : public exception {
    public:
        explicit logic_error(const string& what_arg);
        explicit logic_error(const char* what_arg);
        logic_error(const logic_error& other) noexcept;
        logic_error& operator=(const logic_error& other) noexcept;
        virtual ~logic_error() noexcept;
    };
}
