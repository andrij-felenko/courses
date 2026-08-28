struct drm_msm_gem_submit {          /* DRM_MSM_GEM_SUBMIT = 0x06 */
    __u32 flags;                     /* MSM_PIPE_* | MSM_SUBMIT_* */
    __u32 fence;                     /* out: номер у черзі        */
    __u32 nr_bos, nr_cmds;
    __u64 bos, cmds;
    __s32 fence_fd;                  /* in/out sync_file          */
    __u32 queueid;
    __u64 in_syncobjs, out_syncobjs;
    __u32 nr_in_syncobjs, nr_out_syncobjs, syncobj_stride, pad;
};

struct drm_msm_syncobj { __u32 handle, flags; __u64 point; };  /* MSM_SYNCOBJ_RESET 0x1 */
