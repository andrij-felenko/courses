/* C: розмітка стадій конвеєра за допомогою NVTX */
#include <nvtx3/nvToolsExt.h>

void trace_chunk_execution(int chunk_id, cudaStream_t stream) {
    nvtxRangePushA("Pipeline_Stage_H2D");
    /* Асинхронне копіювання */
    nvtxRangePop();

    nvtxRangePushA("Pipeline_Stage_Compute");
    /* Запуск ядра */
    nvtxRangePop();
}
