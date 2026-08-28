/* Алгоритм закриття дескрипторів ядра, виражений на C++ */
#include <vector>

struct SimulatedKernelFile {
    int refcount{1};
    void close() { /* вивільнення ресурсу */ }
};

void simulate_do_close_on_exec(std::vector<SimulatedKernelFile*>& fds, 
                               std::vector<bool>& cloexec_mask) {
    for (size_t fd = 0; fd < fds.size(); ++fd) {
        if (cloexec_mask[fd] && fds[fd] != nullptr) {
            cloexec_mask[fd] = false;
            SimulatedKernelFile* file = fds[fd];
            fds[fd] = nullptr;
            file->close();
        }
    }
}
