// Перевірка підтримки NUMA (повертає -1, якщо вимкнено або не підтримується)
int numa_available(void);

// Максимальний номер NUMA-вузла в системі (наприклад, 1 для двосокетного сервера)
int numa_max_node(void);

// Кількість налаштованих та доступних вузлів
int numa_num_configured_nodes(void);

// Кількість наявних процесорних ядер у системі
int numa_num_configured_cpus(void);

// Отримання розміру пам'яті вузла та обсягу вільної пам'яті
long long numa_node_size64(int node, long long *freep);

// Відносна дистанція між двома вузлами за таблицею SLIT (10 = локально, 21 = сусід)
int numa_distance(int node1, int node2);
