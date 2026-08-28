#include <scx/common.bpf.h>

#define MAX_CCX_DOMAINS 8

// Структурні дані для відстеження стану задачі в LAVD
struct lavd_task_ctx {
    u64 vdeadline;
    u64 last_run_ts;
    u32 lat_criticality; // Коефіцієнт чутливості до затримки LatencyScale, 0..100
    u32 ccx_id;          // Домен CCX / L3-кеш
};

// BPF Task Storage для збереження контексту LAVD прямо в struct task_struct
struct {
    __uint(type, BPF_MAP_TYPE_TASK_STORAGE);
    __uint(map_flags, BPF_F_NO_PREALLOC);
    __type(key, int);
    __type(value, struct lavd_task_ctx);
} task_ctx_map SEC(".maps");

// Ідентифікатори кастомних DSQ для кожного CCX домену
u64 ccx_dsq_ids[MAX_CCX_DOMAINS];

s32 BPF_STRUCT_OPS(lavd_select_cpu, struct task_struct *p, s32 prev_cpu, u64 wake_flags)
{
    struct lavd_task_ctx *ctx;
    bool is_idle = false;

    ctx = bpf_task_storage_get(&task_ctx_map, p, 0, 0);

    // Якщо задача критична до затримки, утримуємо її на тому ж CPU для збереження L3-кешу
    if (ctx && ctx->lat_criticality > 50)
        return prev_cpu;

    // Інакше — стандартна евристика ядра; is_idle каже, чи обране ядро простоює
    return scx_bpf_select_cpu_dfl(p, prev_cpu, wake_flags, &is_idle);
}

void BPF_STRUCT_OPS(lavd_enqueue, struct task_struct *p, u64 enq_flags)
{
    struct lavd_task_ctx *ctx;
    u64 dsq_id = SCX_DSQ_GLOBAL;

    ctx = bpf_task_storage_get(&task_ctx_map, p, 0, 0);
    if (ctx && ctx->ccx_id < MAX_CCX_DOMAINS) {
        // Призначити в кастомну чергу відповідного CCX домену
        dsq_id = ccx_dsq_ids[ctx->ccx_id];
    }

    // Диспетчеризація задачі із розрахованим квантом
    scx_bpf_dispatch(p, dsq_id, SCX_SLICE_DFL, enq_flags);
}

SEC(".struct_ops.link")
struct sched_ext_ops lavd_ops = {
    .select_cpu = (void *)lavd_select_cpu,
    .enqueue    = (void *)lavd_enqueue,
    .name       = "lavd",
};
