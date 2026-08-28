class monotonic_buffer_resource : public memory_resource {
public:
    monotonic_buffer_resource();
    explicit monotonic_buffer_resource(memory_resource* upstream);
    explicit monotonic_buffer_resource(std::size_t initial_size);
    monotonic_buffer_resource(std::size_t initial_size, memory_resource* upstream);
    monotonic_buffer_resource(void* buffer, std::size_t buffer_size);
    monotonic_buffer_resource(void* buffer, std::size_t buffer_size, memory_resource* upstream);

    virtual ~monotonic_buffer_resource();

    void release();
    memory_resource* upstream_resource() const;
};
