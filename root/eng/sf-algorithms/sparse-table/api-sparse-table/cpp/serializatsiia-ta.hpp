/* Інтерфейс серіалізації та mmap-відображення мовою C++ */
struct alignas(8) FileHeader {
    std::array<char, 4> magic{'S', 'P', 'T', 'B'};
    std::uint32_t version{1};
    std::uint32_t element_size{sizeof(std::int32_t)};
    std::uint64_t n{0};
    std::uint32_t levels{0};
    std::uint32_t flags{0};
    std::uint64_t checksum{0};
};

template <typename T>
bool save_to_file(const SparseTable<T>& st, std::string_view path);

template <typename T>
std::optional<SparseTable<T>> load_from_mmap(std::string_view path);
