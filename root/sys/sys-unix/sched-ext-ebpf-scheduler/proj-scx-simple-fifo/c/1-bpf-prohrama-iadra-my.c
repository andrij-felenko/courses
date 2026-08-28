#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <scx/common.bpf.h>   // BPF_STRUCT_OPS та оголошення kfunc-ів scx_bpf_*

// Ліцензія ядра (обов'язкова для BPF struct_ops)
char _license[] SEC("license") = "GPL";

// Ідентифікатор нашої глобальної черги DSQ
#define MY_DSQ_ID 1001

// Лічильник завантажених завдань у мапі
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 1);
    __type(key, u32);
    __type(value, u64);
} stats_map SEC(".maps");

// 1. Хук ініціалізації: створюємо власну чергу DSQ
SEC("struct_ops/my_fifo_init")
s32 BPF_STRUCT_OPS(my_fifo_init)
{
    // Створюємо чергу MY_DSQ_ID на поточному NUMA-вузлі (-1)
    return scx_bpf_create_dsq(MY_DSQ_ID, -1);
}

// 2. Хук enqueue: коли завдання стає готовим, додаємо його в чергу DSQ
SEC("struct_ops/my_fifo_enqueue")
void BPF_STRUCT_OPS(my_fifo_enqueue, struct task_struct *p, u64 enq_flags)
{
    u32 key = 0;
    u64 *cnt = bpf_map_lookup_elem(&stats_map, &key);
    if (cnt) {
        __sync_fetch_and_add(cnt, 1);
    }

    // Додаємо завдання у глобальну чергу MY_DSQ_ID з дефолтним квантом часу (20 мс)
    scx_bpf_dispatch(p, MY_DSQ_ID, SCX_SLICE_DFL, enq_flags);
}

// 3. Хук dispatch: коли CPU звільняється, споживаємо завдання з черги DSQ
SEC("struct_ops/my_fifo_dispatch")
void BPF_STRUCT_OPS(my_fifo_dispatch, s32 cpu, struct task_struct *prev)
{
    // Вилучаємо перше завдання з черги MY_DSQ_ID для виконання на цьому CPU
    scx_bpf_consume(MY_DSQ_ID);
}

// 4. Реєстрація структури sched_ext_ops
SEC(".struct_ops.link")
struct sched_ext_ops fifo_ops = {
    .init     = (void *)my_fifo_init,
    .enqueue  = (void *)my_fifo_enqueue,
    .dispatch = (void *)my_fifo_dispatch,
    .name     = "simple_fifo_demo",
};
