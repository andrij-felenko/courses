#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <stdexcept>
#include <libvirt/libvirt.h>

namespace cluster {

class LibvirtDomainMigrator {
public:
    static void migrate_live(virDomainPtr dom, const std::string& dest_host) {
        if (!dom) {
            throw std::invalid_argument("Некоректний покажчик домену virDomainPtr");
        }

        std::vector<virTypedParameter> params;
        
        virTypedParameter p_uri{};
        p_uri.field = const_cast<char*>(VIR_MIGRATE_PARAM_URI);
        p_uri.type = VIR_TYPED_PARAM_STRING;
        p_uri.value.s = const_cast<char*>(dest_host.c_str());
        params.push_back(p_uri);

        virTypedParameter p_bw{};
        p_bw.field = const_cast<char*>(VIR_MIGRATE_PARAM_BANDWIDTH);
        p_bw.type = VIR_TYPED_PARAM_ULLONG;
        p_bw.value.ul = 10000; // 10 Гбіт/с
        params.push_back(p_bw);

        virTypedParameter p_par{};
        p_par.field = const_cast<char*>(VIR_MIGRATE_PARAM_PARALLEL_CONNECTIONS);
        p_par.type = VIR_TYPED_PARAM_INT;
        p_par.value.i = 8;
        params.push_back(p_par);

        constexpr unsigned int flags = VIR_MIGRATE_LIVE | 
                                      VIR_MIGRATE_PEER2PEER | 
                                      VIR_MIGRATE_POSTCOPY | 
                                      VIR_MIGRATE_AUTO_CONVERGE | 
                                      VIR_MIGRATE_PERSIST_DEST | 
                                      VIR_MIGRATE_UNDEFINE_SOURCE;

        std::string dconnuri = "qemu+tcp://" + dest_host + "/system";

        int ret = virDomainMigrateToURI3(dom, dconnuri.c_str(),
                                         params.data(), static_cast<int>(params.size()), flags);
        if (ret < 0) {
            virErrorPtr err = virGetLastError();
            std::string msg = err ? err->message : "Невідома помилка libvirt";
            throw std::runtime_error("Збій міграції віртуальної машини: " + msg);
        }
    }
};

} // namespace cluster
