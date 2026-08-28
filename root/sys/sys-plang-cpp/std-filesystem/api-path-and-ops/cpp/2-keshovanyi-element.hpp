namespace std::filesystem {
    class directory_entry {
    public:
        directory_entry() noexcept = default;
        explicit directory_entry(const std::filesystem::path& p);
        directory_entry(const std::filesystem::path& p, std::error_code& ec);

        void assign(const std::filesystem::path& p);
        void assign(const std::filesystem::path& p, std::error_code& ec);
        void replace_filename(const std::filesystem::path& p);
        void replace_filename(const std::filesystem::path& p, std::error_code& ec);
        void refresh();
        void refresh(std::error_code& ec) noexcept;

        const std::filesystem::path& path() const noexcept;
        operator const std::filesystem::path&() const noexcept;

        bool exists() const;
        bool exists(std::error_code& ec) const noexcept;
        bool is_block_file() const;
        bool is_character_file() const;
        bool is_directory() const;
        bool is_fifo() const;
        bool is_other() const;
        bool is_regular_file() const;
        bool is_socket() const;
        bool is_symlink() const;

        std::uintmax_t file_size() const;
        std::uintmax_t file_size(std::error_code& ec) const noexcept;
        std::uintmax_t hard_link_count() const;
        std::uintmax_t hard_link_count(std::error_code& ec) const noexcept;
        
        file_time_type last_write_time() const;
        file_time_type last_write_time(std::error_code& ec) const noexcept;

        file_status status() const;
        file_status status(std::error_code& ec) const noexcept;
        file_status symlink_status() const;
        file_status symlink_status(std::error_code& ec) const noexcept;

        bool operator==(const directory_entry& rhs) const noexcept;
        bool operator!=(const directory_entry& rhs) const noexcept;
        bool operator<(const directory_entry& rhs) const noexcept;
        bool operator<=(const directory_entry& rhs) const noexcept;
        bool operator>(const directory_entry& rhs) const noexcept;
        bool operator>=(const directory_entry& rhs) const noexcept;
    };
}
