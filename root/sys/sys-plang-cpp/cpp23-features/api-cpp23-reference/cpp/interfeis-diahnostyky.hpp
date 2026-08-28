namespace std {

class stacktrace_entry {
public:
    using native_handle_type = /* implementation-defined */;

    constexpr stacktrace_entry() noexcept;
    constexpr native_handle_type native_handle() const noexcept;
    constexpr explicit operator bool() const noexcept;

    string description() const; // Назва функції (з деманглінгом)
    string source_file() const; // Шлях до файлу сирцевого коду
    uint_least32_t source_line() const; // Номер рядка виклику

    friend constexpr bool operator==(const stacktrace_entry&, const stacktrace_entry&) noexcept;
    friend constexpr strong_ordering operator<=>(const stacktrace_entry&, const stacktrace_entry&) noexcept;
};

template <class Allocator = allocator<stacktrace_entry>>
class basic_stacktrace {
public:
    using value_type = stacktrace_entry;
    using const_reference = const value_type&;
    using size_type = size_t;
    using const_iterator = /* implementation-defined */;

    // Фабричні методи захоплення стека
    static basic_stacktrace current(const Allocator& alloc = Allocator()) noexcept;
    static basic_stacktrace current(size_type skip, const Allocator& alloc = Allocator()) noexcept;
    static basic_stacktrace current(size_type skip, size_type max_depth, const Allocator& alloc = Allocator()) noexcept;

    basic_stacktrace() noexcept;
    size_type size() const noexcept;
    bool empty() const noexcept;

    const_reference operator[](size_type frame_no) const;
    const_reference at(size_type frame_no) const;

    const_iterator begin() const noexcept;
    const_iterator end() const noexcept;
};

using stacktrace = basic_stacktrace<allocator<stacktrace_entry>>;

string to_string(const stacktrace& st);
string to_string(const stacktrace_entry& ste);

} // namespace std
