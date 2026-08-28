#include <stdio.h>
#include <stdlib.h>
#include <libvirt/libvirt.h>

int initiate_vm_migration(virDomainPtr dom, const char *dest_host) {
    virTypedParameter params[4];
    int nparams = 0;

    params[nparams].field = VIR_MIGRATE_PARAM_URI;
    params[nparams].type = VIR_TYPED_PARAM_STRING;
    params[nparams].value.s = (char *)dest_host;
    nparams++;

    params[nparams].field = VIR_MIGRATE_PARAM_BANDWIDTH;
    params[nparams].type = VIR_TYPED_PARAM_ULLONG;
    params[nparams].value.ul = 10000; /* 10 Гбіт/с */
    nparams++;

    params[nparams].field = VIR_MIGRATE_PARAM_PARALLEL_CONNECTIONS;
    params[nparams].type = VIR_TYPED_PARAM_INT;
    params[nparams].value.i = 8;
    nparams++;

    unsigned int flags = VIR_MIGRATE_LIVE | 
                         VIR_MIGRATE_PEER2PEER | 
                         VIR_MIGRATE_POSTCOPY | 
                         VIR_MIGRATE_AUTO_CONVERGE | 
                         VIR_MIGRATE_PERSIST_DEST | 
                         VIR_MIGRATE_UNDEFINE_SOURCE;

    char dconnuri[256];
    snprintf(dconnuri, sizeof(dconnuri), "qemu+tcp://%s/system", dest_host);

    int ret = virDomainMigrateToURI3(dom, dconnuri, params, nparams, flags);
    if (ret < 0) {
        virErrorPtr err = virGetLastError();
        fprintf(stderr, "Помилка міграції: %s\n", err ? err->message : "Невідома помилка");
        return -1;
    }
    return 0;
}
