namespace std::filesystem {
    bool create_directory(const path& p);
    bool create_directory(const path& p, std::error_code& ec) noexcept;

    bool create_directories(const path& p);
    bool create_directories(const path& p, std::error_code& ec);

    bool remove(const path& p);
    bool remove(const path& p, std::error_code& ec) noexcept;

    std::uintmax_t remove_all(const path& p);
    std::uintmax_t remove_all(const path& p, std::error_code& ec);

    void rename(const path& old_p, const path& new_p);
    void rename(const path& old_p, const path& new_p, std::error_code& ec) noexcept;

    void copy(const path& from, const path& to, copy_options options = copy_options::none);
    void copy(const path& from, const path& to, copy_options options, std::error_code& ec);

    bool copy_file(const path& from, const path& to, copy_options options = copy_options::none);
    bool copy_file(const path& from, const path& to, copy_options options, std::error_code& ec);
}
