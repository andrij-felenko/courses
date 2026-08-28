static const struct drm_driver my_npu_drm_driver = {
    .driver_features = DRIVER_COMPUTE_ACCEL | DRIVER_GEM,
    .name = "intel_vpu",
    .desc = "Intel Versatile Processing Unit / NPU",
    .major = 1,
    .minor = 0,
    .fops = &accel_driver_fops,
    .ioctls = npu_private_ioctls,
    .num_ioctls = ARRAY_SIZE(npu_private_ioctls),
};
