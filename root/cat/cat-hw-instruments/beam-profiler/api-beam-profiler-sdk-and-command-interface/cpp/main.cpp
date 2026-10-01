#include <beam_profiler.h>
#include <stdio.h>

int main() {
    bp_handle_t profiler = NULL;
    bp_status_t status = BP_SUCCESS;

    // Відкриття сесії підключення до оптичного аналізатора
    status = BeamProfiler_Open(&profiler, 0);
    if (status != BP_SUCCESS) {
        printf("Помилка ініціалізації пристрою: %d\n", status);
        return -1;
    }

    // Встановлення часу витримки 1500 мікросекунд та нульового підсилення
    BeamProfiler_SetExposure(profiler, 1500.0); // мкс
    BeamProfiler_SetGain(profiler, 1.0);

    printf("Пристрій успішно ініціалізовано.\n");
    BeamProfiler_Close(profiler);
    return 0;
}
