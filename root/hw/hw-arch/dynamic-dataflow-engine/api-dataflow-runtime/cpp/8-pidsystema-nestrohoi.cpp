namespace dataflow {

class IStructure {
public:
    static std::expected<std::unique_ptr<IStructure>, Status> create(size_t element_count);
    virtual ~IStructure() = default;

    virtual Status read_async(size_t index, Token consumer_token) noexcept = 0;
    virtual Status write(Engine* engine, size_t index, uint64_t value) noexcept = 0;
    [[nodiscard]] virtual size_t size() const noexcept = 0;
};

} // namespace dataflow
