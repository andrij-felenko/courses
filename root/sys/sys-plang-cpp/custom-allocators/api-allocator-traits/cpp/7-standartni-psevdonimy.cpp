namespace std::pmr {
    template <class T>
    using vector = std::vector<T, polymorphic_allocator<T>>;

    template <class charT, class traits = std::char_traits<charT>>
    using basic_string = std::basic_string<charT, traits, polymorphic_allocator<charT>>;

    using string = basic_string<char>;
    using wstring = basic_string<wchar_t>;

    template <class T>
    using list = std::list<T, polymorphic_allocator<T>>;

    template <class Key, class T, class Compare = std::less<Key>>
    using map = std::map<Key, T, Compare, polymorphic_allocator<std::pair<const Key, T>>>;

    template <class Key, class T, class Hash = std::hash<Key>, class KeyEqual = std::equal_to<Key>>
    using unordered_map = std::unordered_map<Key, T, Hash, KeyEqual, polymorphic_allocator<std::pair<const Key, T>>>;
}
