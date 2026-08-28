namespace std {

template <class CharT, class Traits = char_traits<CharT>>
class basic_spanstream : public basic_iostream<CharT, Traits> {
public:
    using char_type = CharT;
    using traits_type = Traits;
    using int_type = typename traits_type::int_type;
    using pos_type = typename traits_type::pos_type;
    using off_type = typename traits_type::off_type;

    explicit basic_spanstream(span<CharT> s, ios_base::openmode which = ios_base::in | ios_base::out);
    span<CharT> span() const noexcept;
    void span(span<CharT> s) noexcept;
};

using spanstream = basic_spanstream<char>;
using ispanstream = basic_ispanstream<char>;
using ospanstream = basic_ospanstream<char>;

} // namespace std
