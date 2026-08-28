namespace std::filesystem {
    bool exists(file_status s) noexcept;
    bool exists(const path& p);
    bool exists(const path& p, std::error_code& ec) noexcept;

    bool is_regular_file(const path& p);
    bool is_regular_file(const path& p, std::error_code& ec) noexcept;

    bool is_directory(const path& p);
    bool is_directory(const path& p, std::error_code& ec) noexcept;

    bool is_symlink(const path& p);
    bool is_symlink(const path& p, std::error_code& ec) noexcept;

    bool is_empty(const path& p);
    bool is_empty(const path& p, std::error_code& ec);

    bool equivalent(const path& p1, const path& p2);
    bool equivalent(const path& p1, const path& p2, std::error_code& ec) noexcept;

    std::uintmax_t file_size(const path& p);
    std::uintmax_t file_size(const path& p, std::error_code& ec) noexcept;

    file_status status(const path& p);
    file_status status(const path& p, std::error_code& ec) noexcept;

    file_status symlink_status(const path& p);
    file_status symlink_status(const path& p, std::error_code& ec) noexcept;

    space_info space(const path& p);
    space_info space(const path& p, std::error_code& ec) noexcept;
}
