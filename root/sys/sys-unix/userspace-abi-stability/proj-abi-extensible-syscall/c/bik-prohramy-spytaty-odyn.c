struct pacer_info {
        __u32          size;             /* вхід: sizeof у програми; вихід: sizeof у ядра */
        __u32          __reserved0;
        __aligned_u64  flags_supported;  /* які біти прапорців розуміє це ядро */
        __aligned_u64  attrs_supported;  /* бітова мапа відомих типів атрибутів */
        __u32          policy_size;      /* sizeof(struct pacer_policy) у ядрі */
        __u32          __reserved1;
};

#define PACER_INFO_SIZE_VER0  32
