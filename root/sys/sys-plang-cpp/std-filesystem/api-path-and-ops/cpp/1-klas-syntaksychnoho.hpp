namespace std::filesystem {
    class path {
    public:
        using value_type = /* char для POSIX, wchar_t для Windows */;
        using string_type = std::basic_string<value_type>;
        static constexpr value_type preferred_separator = /* '/' для POSIX, '\\' для Windows */;

        // Конструктори та присвоєння
        path() noexcept;
        path(const path& p);
        path(path&& p) noexcept;
        template <class Source> path(const Source& source);
        template <class InputIt> path(InputIt first, InputIt last);

        // Присвоєння та модифікатори
        path& operator=(const path& p);
        path& operator=(path&& p) noexcept;
        path& assign(const string_type& source);
        path& operator/=(const path& p);
        path& append(const path& p);
        path& operator+=(const path& p);
        path& concat(const path& p);
        void clear() noexcept;
        path& make_preferred();
        path& remove_filename();
        path& replace_filename(const path& replacement);
        path& replace_extension(const path& replacement = path());
        void swap(path& rhs) noexcept;

        // Конверсії та представлення в пам'яті
        const string_type& native() const noexcept;
        const value_type* c_str() const noexcept;
        operator string_type() const;

        std::string string() const;
        std::wstring wstring() const;
        std::u8string u8string() const;
        std::u16string u16string() const;
        std::u32string u32string() const;

        // Компоненти синтаксичної декомпозиції
        path root_name() const;
        path root_directory() const;
        path root_path() const;
        path relative_path() const;
        path parent_path() const;
        path filename() const;
        path stem() const;
        path extension() const;

        // Синтаксичні перевірки
        bool empty() const noexcept;
        bool has_root_name() const;
        bool has_root_directory() const;
        bool has_root_path() const;
        bool has_relative_path() const;
        bool has_parent_path() const;
        bool has_filename() const;
        bool has_stem() const;
        bool has_extension() const;
        bool is_absolute() const;
        bool is_relative() const;

        // Нормалізація та ітератори
        path lexically_normal() const;
        path lexically_relative(const path& base) const;
        path lexically_proximate(const path& base) const;

        class iterator;
        using const_iterator = iterator;
        iterator begin() const;
        iterator end() const;
    };
}
