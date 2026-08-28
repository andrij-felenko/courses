struct percpu_data {
    void *ptrs[NR_CPUS];
    void *blkp;
};

#define per_cpu_ptr(ptr, cpu)                                             \
({                                                                        \
    struct percpu_data *__p = (struct percpu_data *)~(unsigned long)(ptr); \
    (__typeof__(ptr))__p->ptrs[(cpu)];                                     \
})
