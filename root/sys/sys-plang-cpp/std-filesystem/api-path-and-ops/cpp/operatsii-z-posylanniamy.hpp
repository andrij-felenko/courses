namespace std::filesystem {
    path canonical(const path& p);
    path canonical(const path& p, std::error_code& ec);

    path weakly_canonical(const path& p);
    path weakly_canonical(const path& p, std::error_code& ec);

    path read_symlink(const path& p);
    path read_symlink(const path& p, std::error_code& ec);

    void create_symlink(const path& target, const path& link);
    void create_symlink(const path& target, const path& link, std::error_code& ec) noexcept;

    void create_hard_link(const path& target, const path& link);
    void create_hard_link(const path& target, const path& link, std::error_code& ec) noexcept;
}
