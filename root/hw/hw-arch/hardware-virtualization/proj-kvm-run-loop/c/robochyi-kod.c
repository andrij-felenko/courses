#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/kvm.h>

int main(void)
{
    /* 1. Відкрити пристрій KVM і звірити версію інтерфейсу. */
    int kvm = open("/dev/kvm", O_RDWR | O_CLOEXEC);
    if (kvm < 0) { perror("open /dev/kvm"); return 1; }

    if (ioctl(kvm, KVM_GET_API_VERSION, 0) != 12) {
        fprintf(stderr, "чужа версія KVM API\n"); return 1;
    }
