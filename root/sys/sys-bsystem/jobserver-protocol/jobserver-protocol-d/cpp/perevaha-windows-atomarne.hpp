// Атомарне мультиплексування токена та процесів у C++
#include <windows.h>
#include <span>
#include <vector>

DWORD wait_for_job_or_process(HANDLE sem_handle, std::span<const HANDLE> process_handles) noexcept {
    std::vector<HANDLE> handles;
    handles.reserve(process_handles.size() + 1);
    handles.push_back(sem_handle);
    handles.insert(handles.end(), process_handles.begin(), process_handles.end());

    return ::WaitForMultipleObjects(
        static_cast<DWORD>(handles.size()),
        handles.data(),
        FALSE, // Прокинутися при сигналі БУДЬ-ЯКОГО об'єкта
        INFINITE
    );
}
