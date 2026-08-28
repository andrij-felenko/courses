struct pool_options {
    std::size_t max_blocks_per_chunk = 0;        // Максимальна кількість блоків у чанку
    std::size_t largest_required_pool_block = 0; // Поріг розміру: більші запити обходять пул і йдуть в upstream
};

class unsynchronized_pool_resource : public memory_resource {
public:
    explicit unsynchronized_pool_resource(const pool_options& opts = {}, memory_resource* upstream = get_default_resource());
    explicit unsynchronized_pool_resource(memory_resource* upstream);
    virtual ~unsynchronized_pool_resource();

    void release();
    memory_resource* upstream_resource() const;
    pool_options options() const;
};
