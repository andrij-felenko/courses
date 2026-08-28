namespace std {
    template <typename CharT, 
              typename Traits = std::char_traits<CharT>, 
              typename Allocator = std::allocator<CharT>>
    class basic_string;

    using string = basic_string<char>;
    using u16string = basic_string<char16_t>;
    using u32string = basic_string<char32_t>;
    using wstring = basic_string<wchar_t>;
}
