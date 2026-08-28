// Приклад інтеграції через C++ FFI заголовок
extern "C" {
    struct HKStatsFFI {
        int32_t total_clusters;
        int32_t total_occupied_sites;
        int32_t max_cluster_size;
        double mean_cluster_size;
        double cluster_density;
        bool has_spanning_cluster_x;
        bool has_spanning_cluster_y;
        bool has_spanning_cluster_z;
    };
}
