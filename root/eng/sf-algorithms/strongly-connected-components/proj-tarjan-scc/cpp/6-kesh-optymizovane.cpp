struct CSRGraphCPP {
    int vertex_count{0};
    std::vector<int> row_offsets; // Size V + 1
    std::vector<int> column_indices; // Size E

    [[nodiscard]] std::span<const int> neighbors(int u) const noexcept {
        return std::span<const int>(
            column_indices.data() + row_offsets[u],
            row_offsets[u + 1] - row_offsets[u]
        );
    }
};
