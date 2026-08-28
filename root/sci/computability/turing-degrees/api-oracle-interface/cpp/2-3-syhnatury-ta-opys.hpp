namespace otm {

class OracleFactory {
public:
    [[nodiscard]] static std::expected<std::shared_ptr<IOracleProvider>, Status>
    create_finite(std::span<const uint64_t> elements);
};

class OracleEngine {
public:
    [[nodiscard]] std::expected<bool, Status>
    query(IOracleProvider& provider, uint64_t query_val, QueryTrace& trace);
};

} // namespace otm
