// include/linux/types.h
typedef struct {
    int counter;
} atomic_t;

#ifdef CONFIG_64BIT
typedef struct {
    s64 counter;
} atomic64_t;
#endif

// include/linux/atomic/atomic-long.h — окремої структури немає, лише псевдонім
#ifdef CONFIG_64BIT
typedef atomic64_t atomic_long_t;
#else
typedef atomic_t   atomic_long_t;
#endif
