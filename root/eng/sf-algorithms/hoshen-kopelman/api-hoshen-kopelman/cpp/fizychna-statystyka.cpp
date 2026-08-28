struct PercolationStats {
    int total_clusters{0};
    int total_occupied_sites{0};
    int max_cluster_size{0};
    double mean_cluster_size{0.0};
    double cluster_density{0.0};
    bool has_spanning_cluster_x{false};
    bool has_spanning_cluster_y{false};
    bool has_spanning_cluster_z{false};
};
