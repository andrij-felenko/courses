struct drm_xe_exec {                  /* DRM_XE_EXEC = 0x09, DRM_IOW  */
    __u64 extensions;
    __u32 exec_queue_id, num_syncs;   /* черга виконання й довжина syncs */
    __u64 syncs;                      /* масив drm_xe_sync            */
    __u64 address;                    /* адреса пакета у просторі VM  */
    __u16 num_batch_buffer; __u16 pad[3]; __u64 reserved[2];
};

struct drm_xe_sync {
    __u64 extensions;
    __u32 type;    /* SYNCOBJ 0x0, TIMELINE_SYNCOBJ 0x1, USER_FENCE 0x2 */
    __u32 flags;   /* DRM_XE_SYNC_FLAG_SIGNAL (1<<0): заряджаємо, а не чекаємо */
    union { __u32 handle; __u64 addr; };
    __u64 timeline_value;  __u64 reserved[2];
};
