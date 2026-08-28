#include <stdio.h>
#include <libvirt/libvirt.h>

int trigger_snapshot_commit(virDomainPtr dom, const char *disk, const char *base, const char *top) {
    unsigned int flags = VIR_DOMAIN_BLOCK_COMMIT_ACTIVE | VIR_DOMAIN_BLOCK_COMMIT_PIVOT;
    int ret = virDomainBlockCommit(dom, disk, base, top, 0, flags);
    if (ret < 0) {
        virErrorPtr err = virGetLastError();
        fprintf(stderr, "Помилка виклику virDomainBlockCommit: %s\n", 
                err ? err->message : "невідома помилка libvirt");
        return -1;
    }
    return 0;
}
