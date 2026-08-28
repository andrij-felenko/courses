struct [[gnu::packed]] CrashDumpContext {
    uint32_t magic{0xDEADBEEFUL};
    uint32_t resetReason{0};
    uint32_t faultCfsr{0};
    uint32_t faultHfsr{0};
    uint32_t faultMmfar{0};
    uint32_t faultBfar{0};
    uint32_t stackedR0{0};
    uint32_t stackedR1{0};
    uint32_t stackedR2{0};
    uint32_t stackedR3{0};
    uint32_t stackedR12{0};
    uint32_t stackedLr{0};
    uint32_t stackedPc{0};
    uint32_t stackedPsr{0};
    uint32_t crc32{0};
};
