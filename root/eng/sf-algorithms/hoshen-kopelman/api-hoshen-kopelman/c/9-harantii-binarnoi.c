/* Експортний C-заголовок для FFI прив'язок */
#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int32_t total_clusters;
    int32_t total_occupied_sites;
    int32_t max_cluster_size;
    double  mean_cluster_size;
    double  cluster_density;
    bool    has_spanning_cluster_x;
    bool    has_spanning_cluster_y;
    bool    has_spanning_cluster_z;
} hk_stats_ffi_t;

#ifdef __cplusplus
}
#endif
