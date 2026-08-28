// Виділити пам'ять на конкретному вузлі
void* numa_alloc_onnode(size_t size, int node);

// Виділити пам'ять на локальному вузлі поточного потоку
void* numa_alloc_local(size_t size);

// Виділити пам'ять із посторінковим чергуванням між усіма вузлами
void* numa_alloc_interleaved(size_t size);

// Виділити пам'ять із чергуванням за заданою маскою вузлів
void* numa_alloc_interleaved_subset(size_t size, struct bitmask *nodemask);

// Звільнити пам'ять, виділену функціями numa_alloc_*
void numa_free(void *start, size_t size);
