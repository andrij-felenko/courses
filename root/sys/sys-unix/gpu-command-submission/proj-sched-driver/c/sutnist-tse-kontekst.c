int mygpu_ctx_init(struct mygpu_ctx *ctx, struct mygpu_device *dev)
{
    struct drm_gpu_scheduler *sched_list[] = {
        &dev->gfx[0].sched, &dev->gfx[1].sched,   /* однакові рушії */
    };

    return drm_sched_entity_init(&ctx->entity, DRM_SCHED_PRIORITY_NORMAL,
                                 sched_list, ARRAY_SIZE(sched_list),
                                 &ctx->guilty);
}

void mygpu_ctx_fini(struct mygpu_ctx *ctx)
{
    drm_sched_entity_destroy(&ctx->entity);  /* flush, а потім fini */
    mygpu_vm_put(ctx->vm);                   /* аж тепер можна віддавати решту */
}
