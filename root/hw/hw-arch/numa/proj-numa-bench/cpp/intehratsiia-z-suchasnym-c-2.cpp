// Використання в C++: передача ресурсу пам'яті в контейнер std::pmr::vector
void process_node_data(int node_id) {
    NumaMemoryResource node_res(node_id);
    
    // Вектор гарантовано виділяє внутрішній динамічний буфер на node_id
    std::pmr::vector<std::uint64_t> vec(&node_res);
    vec.reserve(1'000'000);
    for (std::size_t i = 0; i < 1'000'000; ++i) {
        vec.push_back(i);
    }
}
