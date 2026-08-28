struct sock_filter bpf_code[] = {
    { 0x28, 0, 0, 0x0000000c },
    { 0x15, 0, 1, 0x00000800 },
    { 0x30, 0, 0, 0x00000017 },
    { 0x15, 0, 3, 0x00000006 },
    { 0x28, 0, 0, 0x00000014 },
    { 0x45, 1, 0, 0x00001fff },
    { 0xb1, 0, 0, 0x0000000e },
    { 0x48, 0, 0, 0x0000000e },
    { 0x15, 2, 0, 0x00000050 },
    { 0x48, 0, 0, 0x00000010 },
    { 0x15, 0, 1, 0x00000050 },
    { 0x6, 0, 0, 0x00040000 },
    { 0x6, 0, 0, 0x00000000 },
};

struct sock_fprog bpf_prog;
bpf_prog.len = sizeof(bpf_code) / sizeof(bpf_code[0]);
bpf_prog.filter = bpf_code;

if (setsockopt(fd, SOL_SOCKET, SO_ATTACH_FILTER, &bpf_prog, sizeof(bpf_prog)) < 0) {
    perror("setsockopt SO_ATTACH_FILTER");
}
