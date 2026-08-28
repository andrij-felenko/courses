struct drm_amdgpu_cs_chunk_ib      ib  = { .va_start = va, .ib_bytes = pkt_bytes,
                                           .ip_type  = AMDGPU_HW_IP_GFX };
struct drm_amdgpu_cs_chunk_syncobj sig = { .handle = out_syncobj };

struct drm_amdgpu_cs_chunk chunks[2] = {
    { AMDGPU_CHUNK_ID_IB,          sizeof(ib)  / 4, (uintptr_t)&ib  },
    { AMDGPU_CHUNK_ID_SYNCOBJ_OUT, sizeof(sig) / 4, (uintptr_t)&sig },
};
uint64_t ptrs[2] = { (uintptr_t)&chunks[0], (uintptr_t)&chunks[1] };

union drm_amdgpu_cs cs = { .in = { .ctx_id = ctx_id, .num_chunks = 2,
                                   .chunks = (uintptr_t)ptrs } };

int r = drmIoctl(fd, DRM_IOCTL_AMDGPU_CS, &cs);
/* r == 0 → cs.out.handle — номер завдання; огорожа сама лягла в out_syncobj */
