/* 1. Останнє «ще чогось чекаємо?». NULL означає «можна пускати». */
static struct dma_fence *mygpu_prepare_job(struct drm_sched_job *sched_job,
                                           struct drm_sched_entity *entity)
{
    struct mygpu_job *job = to_mygpu_job(sched_job);

    return mygpu_vm_pending_fence(job->ctx->vm);  /* сторінкові таблиці ще пишуться */
}

/* 2. Покласти в кільце й віддати апаратну огорожу. */
static struct dma_fence *mygpu_run_job(struct drm_sched_job *sched_job)
{
    struct mygpu_job *job = to_mygpu_job(sched_job);
    struct dma_fence *hw;

    if (sched_job->s_fence->finished.error || atomic_read(&job->ctx->guilty))
        return NULL;                 /* після скидання нічого не пускаємо */

    hw = mygpu_ring_emit(job->ctx->ring, job->batch_addr, job->batch_size);
    if (IS_ERR(hw))
        return hw;                   /* завдання спрацює з цією помилкою */

    job->hw_fence = hw;              /* наше посилання — до free_job */
    return dma_fence_get(hw);        /* друге — планувальникові, він його поверне */
}

/* 3. Строк вийшов. */
static enum drm_gpu_sched_stat mygpu_timedout_job(struct drm_sched_job *sched_job)
{
    struct mygpu_job *job = to_mygpu_job(sched_job);
    struct drm_gpu_scheduler *sched = sched_job->sched;

    /* Може, воно не зависло, а лише повільне: лічильник рушія посувається. */
    if (mygpu_ring_progressing(job->ctx->ring))
        return DRM_GPU_SCHED_STAT_NO_HANG;

    drm_sched_stop(sched, sched_job);          /* спинити подання на цьому рушії */
    atomic_set(&job->ctx->guilty, 1);          /* контекст утрачено назавжди */

    if (mygpu_reset_context(job->ctx) < 0 &&   /* спершу пробуємо вузьке скидання */
        mygpu_reset_engine(job->ctx->ring) < 0) {
        drm_sched_start(sched, -ENODEV);
        return DRM_GPU_SCHED_STAT_ENODEV;      /* залізо не піднялося */
    }

    drm_sched_start(sched, -ECANCELED);        /* зняті завдання падають з помилкою */
    return DRM_GPU_SCHED_STAT_RESET;
}

/* 4. Прибрати за завданням. */
static void mygpu_free_job(struct drm_sched_job *sched_job)
{
    struct mygpu_job *job = to_mygpu_job(sched_job);

    dma_fence_put(job->hw_fence);
    drm_sched_job_cleanup(sched_job);   /* огорожі, масив залежностей */
    kfree(job);
}
