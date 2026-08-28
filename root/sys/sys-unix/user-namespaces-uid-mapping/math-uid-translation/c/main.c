struct uid_gid_map {
    u32 nr_extents;
    union {
        struct uid_gid_extent extent[UID_GID_MAP_MAX_BASE_EXTENTS];
        struct {
            struct uid_gid_extent *forward;
            struct uid_gid_extent *reverse;
        };
    };
};
