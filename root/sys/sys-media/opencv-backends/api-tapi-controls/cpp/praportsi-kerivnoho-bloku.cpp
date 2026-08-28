enum UMatData::MemoryFlag {
    COPY_ON_MAP          = 1,
    HOST_COPY_OBSOLETE   = 2,
    DEVICE_COPY_OBSOLETE = 4,
    TEMP_UMAT            = 8,
    TEMP_COPIED_UMAT     = 24,
    USER_ALLOCATED       = 32,
    DEVICE_MEM_MAPPED    = 64,
    ASYNC_CLEANUP        = 128
};
