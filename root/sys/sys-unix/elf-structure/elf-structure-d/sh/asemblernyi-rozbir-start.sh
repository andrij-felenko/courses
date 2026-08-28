$ objdump -d /bin/ls | grep -A 15 "<_start>:"
00000000000068b0 <_start>:
    68b0:   31 ed                   xor    %ebp,%ebp
    68b2:   49 89 d1                mov    %rdx,%r9        # auxv / ld.so cleanup
    68b5:   5e                      pop    %rsi            # rsi = argc
    68b6:   48 89 e2                mov    %rsp,%rdx       # rdx = argv
    68b9:   48 83 e4 f0             and    $0xfffffffffffffff0,%rsp # 16-byte alignment
    68bd:   50                      push   %rax
    68be:   54                      push   %rsp
    68bf:   4c 8d 05 ...            lea    ...(%rip),%r8   # __libc_csu_fini
    68c6:   48 8d 0d ...            lea    ...(%rip),%rcx  # __libc_csu_init
    68cd:   48 8d 3d ...            lea    ...(%rip),%rdi  # main
    68d4:   ff 15 ...               callq  *...(%rip)      # __libc_start_main
    68da:   f4                      hlt
