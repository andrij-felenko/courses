/* Концептуальна модель дескрипторної таблиці ядра у C++ */
#include <vector>
#include <memory>
#include <atomic>

struct FileDescription; // Представлення системного struct file

struct ProcessFdTable {
    unsigned int max_fds{64};
    std::vector<FileDescription*> open_files;
    std::vector<bool> close_on_exec_mask;
    std::vector<bool> allocated_mask;
};
