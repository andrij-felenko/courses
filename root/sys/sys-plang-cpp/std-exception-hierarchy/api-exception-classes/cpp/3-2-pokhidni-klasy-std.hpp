namespace std {
    class system_error : public runtime_error {
    public:
        system_error(error_code ec, const string& what_arg);
        system_error(error_code ec, const char* what_arg);
        system_error(error_code ec);
        system_error(int ev, const error_category& ecat, const string& what_arg);
        system_error(int ev, const error_category& ecat, const char* what_arg);
        system_error(int ev, const error_category& ecat);

        const error_code& code() const noexcept;
        virtual const char* what() const noexcept override;
    };
}
