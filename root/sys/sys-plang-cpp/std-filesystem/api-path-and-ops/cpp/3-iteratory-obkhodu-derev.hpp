namespace std::filesystem {
    enum class directory_options : std::uint16_t {
        none                     = 0,
        follow_directory_symlinks = 1,
        skip_permission_denied   = 2
    };

    constexpr directory_options operator|(directory_options lhs, directory_options rhs);
    constexpr directory_options operator&(directory_options lhs, directory_options rhs);
    constexpr directory_options operator^(directory_options lhs, directory_options rhs);
    constexpr directory_options operator~(directory_options val);
}
