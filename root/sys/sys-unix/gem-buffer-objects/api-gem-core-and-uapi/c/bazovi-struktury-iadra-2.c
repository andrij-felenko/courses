/* include/drm/drm_gem_shmem_helper.h */
struct drm_gem_shmem_object {
    struct drm_gem_object base;
    struct mutex pages_lock;
    struct page **pages;
    unsigned int pages_use_count;
    atomic_t pages_pin_count;
    struct sg_table *sgt;
    struct iosys_map map;
    unsigned int vaddr_use_count;
    bool is_iomem;
};
