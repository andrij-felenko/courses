// Прив'язати виконання поточного процесу/потоку до ядер вказаного вузла
int numa_run_on_node(int node);

// Прив'язати виконання до маски ядер
int numa_run_on_node_mask(struct bitmask *nodemask);

// Встановити жорстку прив'язку виконання і пам'яті (CPU + Memory Bind)
void numa_bind(struct bitmask *nodemask);

// Встановити бажаний вузол для виділення пам'яті
void numa_set_preferred(int node);

// Встановити маску для чергування сторінок у поточному потоці
void numa_set_interleave_mask(struct bitmask *nodemask);
