int mygpu_submit_ioctl(struct drm_device *drm, void *data, struct drm_file *file)
{
    struct drm_mygpu_submit *args = data;
    struct mygpu_ctx *ctx = mygpu_ctx_lookup(file, args->ctx_id);
    struct mygpu_job *job;
    struct dma_fence *out_fence;
    unsigned int i;
    int ret;

    if (atomic_read(&ctx->guilty))
        return -ECANCELED;                 /* контекст утрачено, беруть новий */

    job = kzalloc(sizeof(*job), GFP_KERNEL);
    if (!job)
        return -ENOMEM;
    job->ctx = ctx;

    ret = drm_sched_job_init(&job->base, &ctx->entity,
                             mygpu_credits(args), file->driver_priv,
                             file->client_id);
    if (ret)
        goto err_free;

    for (i = 0; i < args->num_in_fences; i++) {
        struct dma_fence *in = mygpu_in_fence_get(file, args, i);

        if (IS_ERR(in)) { ret = PTR_ERR(in); goto err_cleanup; }

        /* Забирає посилання назавжди — і коли вдалося, і коли ні. */
        ret = drm_sched_job_add_dependency(&job->base, in);
        if (ret)
            goto err_cleanup;
    }

    job->batch_addr = args->batch_addr;
    job->batch_size = args->batch_size;
    ret = mygpu_reserve_ring_slot(ctx->ring, job);   /* усе, що знадобиться потім */
    if (ret)
        goto err_cleanup;

    mutex_lock(&ctx->lock);
    drm_sched_job_arm(&job->base);                   /* точка неповернення */
    out_fence = dma_fence_get(&job->base.s_fence->finished);
    drm_sched_entity_push_job(&job->base);
    mutex_unlock(&ctx->lock);

    ret = mygpu_out_fence_export(file, args, out_fence);
    dma_fence_put(out_fence);
    return ret;

err_cleanup:
    drm_sched_job_cleanup(&job->base);
err_free:
    kfree(job);
    return ret;
}
