/* oops_parser.c — Аналізатор адрес збою мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void parse_and_decode(const char *filename, const char *vmlinux_path) {
    FILE *f = fopen(filename, "r");
    if (!f) {
        perror("Failed to open crash log");
        return;
    }

    char line[512];
    while (fgets(line, sizeof(line), f)) {
        char *rip_pos = strstr(line, "RIP:");
        if (rip_pos) {
            printf("[+] Found Faulting Instruction Pointer line:\n    %s", line);
            
            char func_name[128];
            unsigned long offset = 0, size = 0;
            
            if (sscanf(rip_pos, "RIP: %*x:%[^+]+0x%lx/0x%lx", func_name, &offset, &size) == 3) {
                printf("[+] Parsed symbol: Function=%s, Offset=0x%lx, Size=0x%lx\n",
                       func_name, offset, size);
                
                if (vmlinux_path && access(vmlinux_path, R_OK) == 0) {
                    char cmd[512];
                    snprintf(cmd, sizeof(cmd), "gdb -batch -ex 'info line *%s+0x%lx' %s 2>/dev/null",
                             func_name, offset, vmlinux_path);
                    printf("[+] Resolving via GDB:\n");
                    fflush(stdout);
                    system(cmd);
                }
            }
        }
    }
    fclose(f);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <dmesg_oops.txt> [vmlinux_path]\n", argv[0]);
        return 1;
    }
    parse_and_decode(argv[1], (argc > 2) ? argv[2] : NULL);
    return 0;
}
