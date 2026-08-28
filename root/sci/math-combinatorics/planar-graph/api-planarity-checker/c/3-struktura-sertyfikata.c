typedef struct KuratowskiPath {
    int u;                  /* Початкова базова вершина */
    int v;                  /* Кінцева базова вершина */
    int* path_vertices;     /* Масив проміжних вершин підрозбиття ребра (довжини length + 1) */
    int length;             /* Кількість ребер у топологічному шляху */
} KuratowskiPath;

typedef struct KuratowskiCertificate {
    KuratowskiType type;    /* Тип знайденої обструкції (K5 або K3,3) */
    int core_vertices[6];   /* Індекси базових вузлів (5 для K5, 6 для K3,3) */
    int core_count;         /* Кількість базових вузлів (5 або 6) */
    KuratowskiPath paths[15]; /* Топологічні шляхи між базовими вузлами (10 для K5, 9 для K3,3) */
    int path_count;         /* Загальна кількість шляхів */
} KuratowskiCertificate;
