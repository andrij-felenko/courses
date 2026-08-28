namespace std::filesystem {
    class file_status {
    public:
        explicit file_status(file_type ft = file_type::none, perms prms = perms::unknown) noexcept;
        file_type type() const noexcept;
        void type(file_type ft) noexcept;
        perms permissions() const noexcept;
        void permissions(perms prms) noexcept;
    };

    struct space_info {
        std::uintmax_t capacity;
        std::uintmax_t free;
        std::uintmax_t available;
    };
}
