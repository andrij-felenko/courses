// User Space C++20 Loader: libbpf C++ Wrapper
#include <iostream>
#include <memory>
#include <stdexcept>
#include <bpf/libbpf.h>

namespace dh::forensics {

class EbpfTracer {
public:
    EbpfTracer(const char* bpf_obj_path) {
        bpf_obj_ = bpf_object__open(bpf_obj_path);
        if (!bpf_obj_) {
            throw std::runtime_error("Failed to open eBPF object file");
        }
        if (bpf_object__load(bpf_obj_)) {
            throw std::runtime_error("Failed to load eBPF program into kernel");
        }
    }

    ~EbpfTracer() {
        if (bpf_obj_) {
            bpf_object__close(bpf_obj_);
        }
    }

private:
    bpf_object* bpf_obj_{nullptr};
};

} // namespace dh::forensics
