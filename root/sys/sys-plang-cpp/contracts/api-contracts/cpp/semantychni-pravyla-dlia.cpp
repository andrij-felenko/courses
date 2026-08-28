class BaseStream {
public:
    virtual ~BaseStream() = default;

    virtual std::size_t read_bytes(std::span<std::byte> dst)
        pre [valid_buffer]: !dst.empty()
        post(bytes_read): bytes_read <= dst.size() = 0;
};

class NonBlockingStream : public BaseStream {
public:
    // Автоматично успадковує pre [valid_buffer] та post(bytes_read)
    // Може повертати 0 байтів, якщо даних ще немає, що цілком відповідає bytes_read <= dst.size()
    std::size_t read_bytes(std::span<std::byte> dst) override;
};
