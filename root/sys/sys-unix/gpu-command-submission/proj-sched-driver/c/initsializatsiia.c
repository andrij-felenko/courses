#include <drm/gpu_scheduler.h>

struct mygpu_job {
    struct drm_sched_job base;      /* спільна частина — далі container_of */
    struct mygpu_ctx    *ctx;
    struct dma_fence    *hw_fence;  /* та сама, що поверне run_job */
    u64 batch_addr;                 /* адреса пакета в просторі контексту */
    u32 batch_size;
};
#define to_mygpu_job(j) container_of((j), struct mygpu_job, base)

static const struct drm_sched_backend_ops mygpu_sched_ops = {
    .prepare_job  = mygpu_prepare_job,
    .run_job      = mygpu_run_job,
    .timedout_job = mygpu_timedout_job,
    .free_job     = mygpu_free_job,
    .cancel_job   = mygpu_cancel_job,
};

int mygpu_engine_init(struct mygpu_engine *eng)
{
    const struct drm_sched_init_args args = {
        .ops          = &mygpu_sched_ops,
        .credit_limit = MYGPU_RING_SLOTS - 4,  /* менше, ніж уміщає кільце */
        .hang_limit   = 0,                     /* завинив раз — і по всьому */
        .timeout      = msecs_to_jiffies(500),
        .timeout_wq   = eng->dev->reset_wq,    /* окрема черга робіт під скидання */
        .score        = NULL,
        .name         = "mygpu-gfx",
        .dev          = eng->dev->drm.dev,
    };

    return drm_sched_init(&eng->sched, &args);
}
