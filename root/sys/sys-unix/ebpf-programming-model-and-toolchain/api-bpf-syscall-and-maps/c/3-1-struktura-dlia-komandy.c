union bpf_attr {
    struct {
        __u32   map_type;        // Тип мапи (enum bpf_map_type)
        __u32   key_size;        // Розмір ключа у байтах (наприклад, sizeof(u32))
        __u32   value_size;      // Розмір значення у байтах (наприклад, sizeof(struct event))
        __u32   max_entries;     // Максимальна кількість елементів мапи
        __u32   map_flags;       // Прапорці створення (BPF_F_NO_PREALLOC, BPF_F_NUMA_NODE)
        __u32   inner_map_fd;    // fd шаблону внутрішньої мапи (для BPF_MAP_TYPE_ARRAY_OF_MAPS)
        __u32   numa_node;       // Ідентифікатор NUMA-вузла при BPF_F_NUMA_NODE
        char    map_name[16];    // Символьна назва мапи для ідентифікації у bpftool
        __u32   btf_fd;          // fd метаданих BTF
        __u32   btf_key_type_id; // BTF type ID для типу ключа
        __u32   btf_value_type_id;// BTF type ID для типу значення
    };
};
