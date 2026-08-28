typedef struct {
    int total_clusters;            /* Загальна кількість незалежних зв'язаних кластерів */
    int total_occupied_sites;      /* Загальна кількість зайнятих вузлів на ґратці */
    int max_cluster_size;          /* Розмір (кількість вузлів) найбільшого знайденого кластера */
    double mean_cluster_size;      /* Зважений середній розмір скінченних кластерів S(p) = M_2 / M_1 */
    double cluster_density;        /* Питома кількість кластерів на один вузол ґратки M_0 = K / N */
    bool has_spanning_cluster_x;   /* Наявність протікання вздовж осі X (зліва направо) */
    bool has_spanning_cluster_y;   /* Наявність протікання вздовж осі Y (згори вниз) */
    bool has_spanning_cluster_z;   /* Наявність протікання вздовж осі Z (вглиб, для 3D) */
} hk_stats_t;
