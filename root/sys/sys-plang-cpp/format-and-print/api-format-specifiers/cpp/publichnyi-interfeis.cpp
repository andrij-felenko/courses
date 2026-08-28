namespace std {
    template <typename CharT>
    struct formatter<MyType, CharT> {
        // 1. Метод розбору специфікатора формату у consteval/constexpr контексті
        constexpr auto parse(basic_format_parse_context<CharT>& ctx) 
            -> typename basic_format_parse_context<CharT>::iterator;

        // 2. Метод запису заформатованого значення у вихідний ітератор під час виконання
        template <typename FormatContext>
        auto format(const MyType& val, FormatContext& ctx) const 
            -> typename FormatContext::iterator;
    };
}
