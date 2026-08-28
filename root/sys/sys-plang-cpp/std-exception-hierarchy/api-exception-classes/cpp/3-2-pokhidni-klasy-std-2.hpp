namespace std::filesystem {
    class filesystem_error : public std::system_error {
    public:
        filesystem_error(const string& what_arg, error_code ec);
        filesystem_error(const string& what_arg, const path& p1, error_code ec);
        filesystem_error(const string& what_arg, const path& p1, const path& p2, error_code ec);

        const path& path1() const noexcept;
        const path& path2() const noexcept;
        virtual const char* what() const noexcept override;
    };
}
