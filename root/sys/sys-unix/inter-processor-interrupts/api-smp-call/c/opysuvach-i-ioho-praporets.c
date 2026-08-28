struct __call_single_node {
        struct llist_node llist;      /* вузол черги цілі             */
        union { unsigned int u_flags; atomic_t a_flags; };
        u16 src, dst;                 /* лише на 64-бітних            */
};

struct __call_single_data {
        struct __call_single_node node;
        smp_call_func_t           func;
        void                     *info;
};
typedef struct __call_single_data call_single_data_t
        __aligned(sizeof(struct __call_single_data));

#define CSD_INIT(_func, _info) \
        (struct __call_single_data){ .func = (_func), .info = (_info), }
#define INIT_CSD(_csd, _func, _info)  do { *(_csd) = CSD_INIT((_func), (_info)); } while (0)
