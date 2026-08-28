enum MemoryFlag {
    COPY_ON_MAP          = 1,
    HOST_COPY_OBSOLETE   = 2,    // копія в системній памʼяті застаріла
    DEVICE_COPY_OBSOLETE = 4,    // копія на пристрої застаріла
    TEMP_UMAT            = 8,
    TEMP_COPIED_UMAT     = 24,
    USER_ALLOCATED       = 32,
    DEVICE_MEM_MAPPED    = 64,
    ASYNC_CLEANUP        = 128
};
