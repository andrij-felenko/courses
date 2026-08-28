union bpf_iter_link_info {
    struct {
        __u32 map_fd;        /* Файловий дескриптор мапи для iter/bpf_map_elem */
    } map;
    struct {
        enum bpf_cgroup_iter_order order; /* Порядок обходу: BPF_CGROUP_ITER_ASC / DESC */
        __u32 cgroup_fd;                  /* Файловий дескриптор цільової cgroup */
        __u64 cgroup_id;                  /* Унікальний числовий ID cgroup у ядрі */
    } cgroup;
    struct {
        __u32 pid;                        /* Цільовий PID для iter/task або iter/task_file */
    } task;
};
