struct drm_syncobj_timeline_wait {   /* v5.2 */
    __u64 handles;        /* масив дескрипторів об'єктів */
    __u64 points;         /* по позначці шкали на кожен  */
    __s64 timeout_nsec;   /* абсолютний час за CLOCK_MONOTONIC */
    __u32 count_handles, flags, first_signaled, pad;
    __u64 deadline_nsec;  /* v6.8 */
};

#define DRM_SYNCOBJ_WAIT_FLAGS_WAIT_ALL        (1 << 0)  /* v4.14 */
#define DRM_SYNCOBJ_WAIT_FLAGS_WAIT_FOR_SUBMIT (1 << 1)  /* v4.14 */
#define DRM_SYNCOBJ_WAIT_FLAGS_WAIT_AVAILABLE  (1 << 2)  /* v5.2  */
#define DRM_SYNCOBJ_WAIT_FLAGS_WAIT_DEADLINE   (1 << 3)  /* v6.8  */
