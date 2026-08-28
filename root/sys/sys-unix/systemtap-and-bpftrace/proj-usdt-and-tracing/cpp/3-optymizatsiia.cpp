// Ідіоматична реалізація мовою C++ з RAII та std::string
#include <sys/sdt.h>
#include <string>
#include <memory>

unsigned short workpool_task_start_semaphore __attribute__ ((unused)) = 0;

void process_complex_task(int task_id) {
    if (STAP_PROBE_INPUT_ENABLED(workpool, task_start)) {
        // Замість ручного malloc/free використовуємо std::string та RAII
        std::string payload = generate_expensive_diagnostics_cpp();
        STAP_PROBE1(workpool, task_start, payload.c_str());
    }
}
