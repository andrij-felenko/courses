struct drm_i915_gem_execbuffer2 {
    __u64 buffers_ptr;         /* масив drm_i915_gem_exec_object2 */
    __u32 buffer_count, batch_start_offset, batch_len;
    __u32 DR1, DR4;            /* мертві з часів DRI1 */
    __u32 num_cliprects;       /* ← довжина масиву огорож при FENCE_ARRAY */
    __u64 cliprects_ptr;       /* ← масив drm_i915_gem_exec_fence або розширення */
    __u64 flags;               /* I915_EXEC_* */
    __u64 rsvd1;               /* ← номер контексту */
    __u64 rsvd2;               /* ← молодші 32 біти: вхідний sync_file fd
                                     старші 32 біти: вихідний sync_file fd */
};
