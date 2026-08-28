/* include/asm-generic/vmlinux.lds.h */
#define INIT_CALLS_LEVEL(level)                          \
                __initcall##level##_start = .;           \
                KEEP(*(.initcall##level##.init))         \
                KEEP(*(.initcall##level##s.init))

#define INIT_CALLS                                       \
                __initcall_start = .;                    \
                KEEP(*(.initcallearly.init))             \
                INIT_CALLS_LEVEL(0)                      \
                ...                                      \
                INIT_CALLS_LEVEL(5)                      \
                INIT_CALLS_LEVEL(rootfs)                 \
                INIT_CALLS_LEVEL(6)                      \
                INIT_CALLS_LEVEL(7)                      \
                __initcall_end = .;
