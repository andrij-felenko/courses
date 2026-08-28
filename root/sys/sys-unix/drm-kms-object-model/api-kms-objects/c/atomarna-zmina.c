struct drm_mode_atomic {
        __u32 flags;
        __u32 count_objs;
        __u64 objs_ptr;            /* __u32[count_objs]  — номери об'єктів */
        __u64 count_props_ptr;     /* __u32[count_objs]  — скільки в кожного */
        __u64 props_ptr;           /* __u32[сума]        — СУЦІЛЬНИЙ масив */
        __u64 prop_values_ptr;     /* __u64[сума]        — той самий порядок */
        __u64 reserved;            /* мусить бути 0 */
        __u64 user_data;           /* вернеться в події незміненим */
};
