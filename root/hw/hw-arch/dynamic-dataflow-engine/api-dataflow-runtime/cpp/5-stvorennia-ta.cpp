namespace dataflow {

class Graph {
public:
    static std::expected<std::unique_ptr<Graph>, Status> create(uint32_t max_nodes);
    virtual ~Graph() = default;

    virtual Status set_node(NodeId node_id, NodeDesc desc) noexcept = 0;
    [[nodiscard]] virtual const NodeDesc* get_node(NodeId node_id) const noexcept = 0;
    [[nodiscard]] virtual size_t node_count() const noexcept = 0;
};

} // namespace dataflow
