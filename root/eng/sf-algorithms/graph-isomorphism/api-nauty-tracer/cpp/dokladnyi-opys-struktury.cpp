// Обгортка статистики в C++ для безпечного читання метрик:
struct NautyStats {
    double aut_group_size;
    int num_orbits;
    unsigned long nodes_visited;
    unsigned long canonical_updates;

    static NautyStats from_c_stats(const statsblk& stats) {
        return NautyStats{
            stats.grpsize1 * std::pow(10.0, stats.grpsize2),
            stats.numorbits,
            stats.numnodes,
            stats.canupdates
        };
    }
};
