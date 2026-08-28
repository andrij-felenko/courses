struct drm_amdgpu_cs_chunk_ib {
    __u32 _pad, flags;      /* AMDGPU_IB_FLAG_*                      */
    __u64 va_start;         /* адреса пакета у просторі контексту    */
    __u32 ib_bytes;         /* довжина в БАЙТАХ (на відміну від length_dw) */
    __u32 ip_type;          /* AMDGPU_HW_IP_GFX 0, COMPUTE 1, DMA 2,
                               UVD 3, VCE 4, UVD_ENC 5, VCN_DEC 6,
                               VCN_ENC 7, VCN_JPEG 8, VPE 9          */
    __u32 ip_instance, ring;
};

struct drm_amdgpu_cs_chunk_dep    { __u32 ip_type, ip_instance, ring, ctx_id; __u64 handle; };
struct drm_amdgpu_cs_chunk_syncobj{ __u32 handle, flags; __u64 point; };
