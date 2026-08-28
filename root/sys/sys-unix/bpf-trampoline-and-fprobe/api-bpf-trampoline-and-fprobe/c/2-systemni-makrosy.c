/* Внутрішня реалізація макросу BPF_PROG у заголовочному файлі bpf_tracing.h */
#define BPF_PROG(name, args...) \
name(unsigned long long *ctx); \
static __attribute__((always_inline)) typeof(name(0)) \
____##name(unsigned long long *ctx, ##args); \
typeof(name(0)) name(unsigned long long *ctx) \
{ \
    return ____##name(ctx, ##args_unpack); \
} \
static __attribute__((always_inline)) typeof(name(0)) \
____##name(unsigned long long *ctx, ##args)
