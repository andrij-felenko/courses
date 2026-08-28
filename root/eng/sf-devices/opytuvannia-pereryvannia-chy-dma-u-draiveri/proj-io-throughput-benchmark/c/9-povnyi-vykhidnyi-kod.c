#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>
#include <math.h>

// ============================================================================
// 1. АПАРАТНА АРХІТЕКТУРА ТА РЕГІСТРИ ARM CORTEX-M
// ============================================================================

typedef struct {
    volatile uint32_t CTRL;    // 0xE0001000 DWT Control Register
    volatile uint32_t CYCCNT;  // 0xE0001004 DWT Cycle Count Register
    volatile uint32_t CPICNT;  // 0xE0001008 CPI Count Register
    volatile uint32_t EXCCNT;  // 0xE000100C Exception Overhead Count Register
    volatile uint32_t SLEEPCNT;// 0xE0001010 Sleep Count Register
    volatile uint32_t LSUCNT;  // 0xE0001014 LSU Count Register
    volatile uint32_t FOLDCNT; // 0xE0001018 Folded-instruction Count Register
} DwtHardwareBlock_t;

typedef struct {
    volatile uint32_t DHCSR;   // Debug Halting Control and Status Register
    volatile uint32_t DCRSR;   // Debug Core Register Selector Register
    volatile uint32_t DCRDR;   // Debug Core Register Data Register
    volatile uint32_t DEMCR;   // Debug Exception and Monitor Control Register
} CoreDebugBlock_t;

typedef struct {
    volatile uint32_t ICIALLU; // I-Cache Invalidate All to PoU
    volatile uint32_t reserved0;
    volatile uint32_t BPIALL;  // Branch Predictor Invalidate All
    volatile uint32_t reserved1;
    volatile uint32_t ICIALLUIS;
    volatile uint32_t DCCMVAC; // D-Cache Clean by Address to PoC
    volatile uint32_t DCIMVAC; // D-Cache Invalidate by Address to PoC
    volatile uint32_t DCCIMVAC;// D-Cache Clean and Invalidate by Address to PoC
} ScbCacheBlock_t;

#define DWT_BLOCK        ((DwtHardwareBlock_t *)0xE0001000)
#define CORE_DEBUG_BLOCK ((CoreDebugBlock_t *)0xE000EDFC)
#define SCB_CACHE_BLOCK  ((ScbCacheBlock_t *)0xE000EF50)

#define DEMCR_TRCENA_BIT     (1u << 24)
#define DWT_CTRL_CYCCNTENA   (1u << 0)
#define DWT_CTRL_CPIEVTENA   (1u << 17)
#define DWT_CTRL_EXCEVTENA   (1u << 18)

// ============================================================================
// 2. ЕМУЛЯТОР АПАРАТНОЇ ПЕРИФЕРІЇ ТА ШИННОЇ МАТРИЦІ AHB/APB
// ============================================================================

typedef struct {
    volatile uint32_t SR;   // Status Register (TXE, TC, RXNE, ORE, PE)
    volatile uint32_t DR;   // Data Register (8/9 bit)
    volatile uint32_t BRR;  // Baud Rate Register
    volatile uint32_t CR1;  // Control Register 1 (UE, TE, RE, TXEIE, TCIE, RXNEIE)
    volatile uint32_t CR2;  // Control Register 2 (STOP bits)
    volatile uint32_t CR3;  // Control Register 3 (DMAT, DMAR, RTSE, CTSE)
} MockUartHardware_t;

#define MOCK_UART_SR_PE    (1u << 0)
#define MOCK_UART_SR_FE    (1u << 1)
#define MOCK_UART_SR_NE    (1u << 2)
#define MOCK_UART_SR_ORE   (1u << 3)
#define MOCK_UART_SR_IDLE  (1u << 4)
#define MOCK_UART_SR_RXNE  (1u << 5)
#define MOCK_UART_SR_TC    (1u << 6)
#define MOCK_UART_SR_TXE   (1u << 7)

typedef struct {
    volatile uint32_t CR;   // Stream Control Register
    volatile uint32_t NDTR; // Number of Data Register (0..65535)
    volatile uint32_t PAR;  // Peripheral Address Register
    volatile uint32_t M0AR; // Memory 0 Address Register
    volatile uint32_t M1AR; // Memory 1 Address Register (Double Buffer)
    volatile uint32_t FCR;  // FIFO Control Register
} MockDmaStreamHardware_t;

#define MOCK_DMA_CR_EN     (1u << 0)
#define MOCK_DMA_CR_DMEIE  (1u << 1)
#define MOCK_DMA_CR_TEIE   (1u << 2)
#define MOCK_DMA_CR_HTIE   (1u << 3)
#define MOCK_DMA_CR_TCIE   (1u << 4)
#define MOCK_DMA_CR_PFCTRL (1u << 5)
#define MOCK_DMA_CR_CIRC   (1u << 8)
#define MOCK_DMA_CR_MINC   (1u << 10)
#define MOCK_DMA_CR_PINC   (1u << 9)
#define MOCK_DMA_CR_PL_0   (1u << 16)
#define MOCK_DMA_CR_PL_1   (1u << 17)

static MockUartHardware_t g_mock_uart;
static MockDmaStreamHardware_t g_mock_dma;

static void MockPeripheral_Reset(void) {
    g_mock_uart.SR = MOCK_UART_SR_TXE | MOCK_UART_SR_TC;
    g_mock_uart.DR = 0;
    g_mock_uart.BRR = 0x1D4C; // 115200 бод при частоті APB 168 МГц
    g_mock_uart.CR1 = (1u << 13) | (1u << 3) | (1u << 2); // UE | TE | RE
    g_mock_uart.CR2 = 0;
    g_mock_uart.CR3 = (1u << 7); // DMAT (DMA Transmitter Enable)

    g_mock_dma.CR = 0;
    g_mock_dma.NDTR = 0;
    g_mock_dma.PAR = (uint32_t)&g_mock_uart.DR;
    g_mock_dma.M0AR = 0;
    g_mock_dma.M1AR = 0;
    g_mock_dma.FCR = (1u << 2); // Direct Mode Disable (FIFO Enable)
}

// ============================================================================
// 3. ПОТОКОБЕЗПЕЧНИЙ КІЛЬЦЕВИЙ БУФЕР SPSC FIFO
// ============================================================================

#define SPSC_FIFO_CAPACITY 8192
#define SPSC_FIFO_MASK (SPSC_FIFO_CAPACITY - 1)

typedef struct {
    uint8_t buffer[SPSC_FIFO_CAPACITY];
    volatile uint32_t head;
    volatile uint32_t tail;
    volatile uint32_t overruns;
} SpscFifoBuffer_t;

static SpscFifoBuffer_t g_spsc_fifo;

static inline void SpscFifo_Init(SpscFifoBuffer_t *f) {
    f->head = 0;
    f->tail = 0;
    f->overruns = 0;
}

static inline bool SpscFifo_WriteFromIsr(SpscFifoBuffer_t *f, uint8_t byte) {
    uint32_t current_head = f->head;
    uint32_t current_tail = f->tail;

    if (((current_head + 1) & SPSC_FIFO_MASK) == (current_tail & SPSC_FIFO_MASK)) {
        f->overruns++;
        return false; // Буфер переповнено
    }

    f->buffer[current_head & SPSC_FIFO_MASK] = byte;
    __asm volatile ("dmb" ::: "memory");
    f->head = current_head + 1;
    return true;
}

static inline bool SpscFifo_Read(SpscFifoBuffer_t *f, uint8_t *byte) {
    uint32_t current_head = f->head;
    uint32_t current_tail = f->tail;

    if (current_head == current_tail) {
        return false; // Буфер порожній
    }

    *byte = f->buffer[current_tail & SPSC_FIFO_MASK];
    __asm volatile ("dmb" ::: "memory");
    f->tail = current_tail + 1;
    return true;
}

static inline size_t SpscFifo_Count(const SpscFifoBuffer_t *f) {
    uint32_t current_head = f->head;
    uint32_t current_tail = f->tail;
    return (size_t)(current_head - current_tail);
}

// ============================================================================
// 4. СИСТЕМНИЙ ПІДСИСТЕМНИЙ МОДУЛЬ DWT ТА УЗГОДЖЕННЯ D-CACHE
// ============================================================================

static uint32_t g_dwt_calibration_offset = 0;

static void DWT_HardwareBenchmarkInit(void) {
    volatile uint32_t *demcr = (volatile uint32_t *)0xE000EDFC;
    volatile uint32_t *dwt_ctrl = (volatile uint32_t *)0xE0001000;
    *demcr |= DEMCR_TRCENA_BIT;
    *dwt_ctrl |= DWT_CTRL_CYCCNTENA;

    // Калібрування похибки вибірки лічильника
    volatile uint32_t *cyccnt = (volatile uint32_t *)0xE0001004;
    __asm volatile ("isb" ::: "memory");
    __asm volatile ("dsb" ::: "memory");
    uint32_t start = *cyccnt;
    __asm volatile ("isb" ::: "memory");
    __asm volatile ("dsb" ::: "memory");
    uint32_t end = *cyccnt;

    g_dwt_calibration_offset = (end >= start) ? (end - start) : 0;
}

static inline uint32_t DWT_GetCycleCountSafe(void) {
    volatile uint32_t *cyccnt = (volatile uint32_t *)0xE0001004;
    return *cyccnt;
}

static void CacheMaintenance_CleanRange(const void *addr, size_t size) {
    uintptr_t start_addr = (uintptr_t)addr & ~(uintptr_t)0x1F;
    uintptr_t end_addr = ((uintptr_t)addr + size + 0x1F) & ~(uintptr_t)0x1F;

    for (uintptr_t p = start_addr; p < end_addr; p += 32) {
        SCB_CACHE_BLOCK->DCCMVAC = (uint32_t)p;
    }
    __asm volatile ("dsb" ::: "memory");
    __asm volatile ("isb" ::: "memory");
}

static void CacheMaintenance_InvalidateRange(const void *addr, size_t size) {
    uintptr_t start_addr = (uintptr_t)addr & ~(uintptr_t)0x1F;
    uintptr_t end_addr = ((uintptr_t)addr + size + 0x1F) & ~(uintptr_t)0x1F;

    for (uintptr_t p = start_addr; p < end_addr; p += 32) {
        SCB_CACHE_BLOCK->DCIMVAC = (uint32_t)p;
    }
    __asm volatile ("dsb" ::: "memory");
    __asm volatile ("isb" ::: "memory");
}

// ============================================================================
// 5. РЕАЛІЗАЦІЯ ТРЬОХ ЕТАЛОННИХ ДРАЙВЕРІВ
// ============================================================================

// 5.1. POLLING DRIVER: ПОВНЕ СИНХРОННЕ ОПИТУВАННЯ
static uint32_t Driver_ExecutePollingTest(MockUartHardware_t *hw, const uint8_t *payload, size_t length) {
    __asm volatile ("isb" ::: "memory");
    __asm volatile ("dsb" ::: "memory");
    uint32_t start_cycles = DWT_GetCycleCountSafe();

    for (size_t i = 0; i < length; ++i) {
        // Опитування біта готовності передавача TXE
        while (!(hw->SR & MOCK_UART_SR_TXE)) {
            // У виробничому коді тут виконується перевірка таймауту DWT
        }
        hw->DR = payload[i];

        // Симуляція апаратної зміни стану регістра шини APB
        hw->SR &= ~MOCK_UART_SR_TXE;
        hw->SR |= MOCK_UART_SR_TXE;
    }

    // Очікування фізичного звільнення лінії зв'язку (TC - Transmission Complete)
    while (!(hw->SR & MOCK_UART_SR_TC)) {}

    __asm volatile ("dsb" ::: "memory");
    __asm volatile ("isb" ::: "memory");
    uint32_t elapsed = DWT_GetCycleCountSafe() - start_cycles;

    return (elapsed > g_dwt_calibration_offset) ? (elapsed - g_dwt_calibration_offset) : 1;
}

// 5.2. INTERRUPT DRIVER: ПОДІЄВА МОДЕЛЬ З SPSC FIFO ТА СТЕКІНГОМ NVIC
static uint32_t Driver_ExecuteInterruptTest(MockUartHardware_t *hw, SpscFifoBuffer_t *fifo, const uint8_t *payload, size_t length) {
    SpscFifo_Init(fifo);

    __asm volatile ("isb" ::: "memory");
    __asm volatile ("dsb" ::: "memory");
    uint32_t start_cycles = DWT_GetCycleCountSafe();

    // 1. Початкове наповнення черги драйвера (виконується прикладним потоком)
    for (size_t i = 0; i < length; ++i) {
        SpscFifo_WriteFromIsr(fifo, payload[i]);
    }

    // 2. Симуляція апаратного циклу обробника ISR
    uint8_t outgoing_byte;
    while (SpscFifo_Read(fifo, &outgoing_byte)) {
        // Фізична симуляція апаратного стекінгу NVIC ядра Cortex-M:
        // 12 тактів вхід (збереження R0-R3, R12, LR, PC, xPSR) +
        // 12 тактів вихід (розстекування) + пролог/епілог AAPCS (8 тактів) = ~32 такти
        __asm volatile (
            "nop\n nop\n nop\n nop\n nop\n nop\n nop\n nop\n"
            "nop\n nop\n nop\n nop\n nop\n nop\n nop\n nop\n"
            "nop\n nop\n nop\n nop\n nop\n nop\n nop\n nop\n"
            "nop\n nop\n nop\n nop\n nop\n nop\n nop\n nop\n"
            ::: "memory"
        );

        hw->DR = outgoing_byte;
        hw->SR &= ~MOCK_UART_SR_TXE;
        hw->SR |= MOCK_UART_SR_TXE;
    }

    __asm volatile ("dsb" ::: "memory");
    __asm volatile ("isb" ::: "memory");
    uint32_t elapsed = DWT_GetCycleCountSafe() - start_cycles;

    return (elapsed > g_dwt_calibration_offset) ? (elapsed - g_dwt_calibration_offset) : 1;
}

// 5.3. DMA DRIVER: ЦИРКУЛЯРНИЙ ПРЯМИЙ ДОСТУП З ОБСЛУГОВУВАННЯМ КЕШУ
static uint32_t Driver_ExecuteDmaTest(MockDmaStreamHardware_t *dma, MockUartHardware_t *uart, const uint8_t *payload, size_t length) {
    __asm volatile ("isb" ::: "memory");
    __asm volatile ("dsb" ::: "memory");
    uint32_t start_cycles = DWT_GetCycleCountSafe();

    // 1. Безпечна деактивація потоку DMA перед зміною регістрів
    dma->CR &= ~MOCK_DMA_CR_EN;
    __asm volatile ("dsb" ::: "memory");

    // 2. Встановлення адрес периферії, пам'яті та довжини транзакції
    dma->PAR = (uint32_t)&uart->DR;
    dma->M0AR = (uint32_t)payload;
    dma->NDTR = (uint32_t)length;

    // 3. Узгодження кешу даних (Clean D-Cache перед початком передачі)
    CacheMaintenance_CleanRange(payload, length);

    // 4. Конфігурація: інкремент пам'яті, пріоритет High, активація каналу
    dma->CR = MOCK_DMA_CR_MINC | MOCK_DMA_CR_TCIE | MOCK_DMA_CR_PL_1 | MOCK_DMA_CR_EN;
    __asm volatile ("dsb" ::: "memory");

    // 5. Симуляція апаратного перенесення блоку шинною матрицею AHB
    // Процесор не бере участі в перенесенні; генерується лише одне фінальне переривання TCIF
    __asm volatile (
        "nop\n nop\n nop\n nop\n nop\n nop\n nop\n nop\n"
        "nop\n nop\n nop\n nop\n nop\n nop\n nop\n nop\n"
        ::: "memory"
    );
    dma->CR &= ~MOCK_DMA_CR_EN; // Завершення транзакції контролером DMA

    __asm volatile ("dsb" ::: "memory");
    __asm volatile ("isb" ::: "memory");
    uint32_t elapsed = DWT_GetCycleCountSafe() - start_cycles;

    return (elapsed > g_dwt_calibration_offset) ? (elapsed - g_dwt_calibration_offset) : 1;
}

// ============================================================================
// 6. СТАТИСТИЧНИЙ АНАЛІЗ ТА РАННЕР БЕНЧМАРКУ
// ============================================================================

__attribute__((aligned(32))) static uint8_t g_benchmark_payload[4096];

typedef struct {
    size_t payload_size;
    uint32_t poll_min;
    uint32_t poll_med;
    uint32_t poll_p99;
    float poll_cpb;
    uint32_t irq_min;
    uint32_t irq_med;
    uint32_t irq_p99;
    float irq_cpb;
    uint32_t dma_min;
    uint32_t dma_med;
    uint32_t dma_p99;
    float dma_cpb;
} DetailedBenchmarkResult_t;

static const size_t PAYLOAD_SIZE_LIST[] = { 1, 4, 16, 64, 256, 1024, 4096 };
#define TEST_ARRAY_SIZE (sizeof(PAYLOAD_SIZE_LIST) / sizeof(PAYLOAD_SIZE_LIST[0]))
#define BENCH_ITERATION_COUNT 100

static DetailedBenchmarkResult_t g_detailed_results[TEST_ARRAY_SIZE];

static void InsertionSort(uint32_t *arr, size_t n) {
    for (size_t i = 1; i < n; ++i) {
        uint32_t key = arr[i];
        int32_t j = (int32_t)i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}

void Benchmark_ExecuteFullSuite(void) {
    DWT_HardwareBenchmarkInit();
    MockPeripheral_Reset();

    for (size_t i = 0; i < sizeof(g_benchmark_payload); ++i) {
        g_benchmark_payload[i] = (uint8_t)(i ^ 0xAA);
    }

    printf("\n====================================================================================\n");
    printf("   ПРАКТИЧНИЙ БЕНЧМАРК I/O: POLLING vs INTERRUPTS vs DMA (ARM CORTEX-M @ 168 MHz)\n");
    printf("====================================================================================\n\n");

    uint32_t samples[BENCH_ITERATION_COUNT];

    for (size_t idx = 0; idx < TEST_ARRAY_SIZE; ++idx) {
        size_t payload_len = PAYLOAD_SIZE_LIST[idx];
        g_detailed_results[idx].payload_size = payload_len;

        // 1. Серія випробувань Polling
        for (size_t iter = 0; iter < BENCH_ITERATION_COUNT; ++iter) {
            samples[iter] = Driver_ExecutePollingTest(&g_mock_uart, g_benchmark_payload, payload_len);
        }
        InsertionSort(samples, BENCH_ITERATION_COUNT);
        g_detailed_results[idx].poll_min = samples[0];
        g_detailed_results[idx].poll_med = samples[BENCH_ITERATION_COUNT / 2];
        g_detailed_results[idx].poll_p99 = samples[(BENCH_ITERATION_COUNT * 99) / 100];
        g_detailed_results[idx].poll_cpb = (float)g_detailed_results[idx].poll_med / (float)payload_len;

        // 2. Серія випробувань Interrupts
        for (size_t iter = 0; iter < BENCH_ITERATION_COUNT; ++iter) {
            samples[iter] = Driver_ExecuteInterruptTest(&g_mock_uart, &g_spsc_fifo, g_benchmark_payload, payload_len);
        }
        InsertionSort(samples, BENCH_ITERATION_COUNT);
        g_detailed_results[idx].irq_min = samples[0];
        g_detailed_results[idx].irq_med = samples[BENCH_ITERATION_COUNT / 2];
        g_detailed_results[idx].irq_p99 = samples[(BENCH_ITERATION_COUNT * 99) / 100];
        g_detailed_results[idx].irq_cpb = (float)g_detailed_results[idx].irq_med / (float)payload_len;

        // 3. Серія випробувань DMA
        for (size_t iter = 0; iter < BENCH_ITERATION_COUNT; ++iter) {
            samples[iter] = Driver_ExecuteDmaTest(&g_mock_dma, &g_mock_uart, g_benchmark_payload, payload_len);
        }
        InsertionSort(samples, BENCH_ITERATION_COUNT);
        g_detailed_results[idx].dma_min = samples[0];
        g_detailed_results[idx].dma_med = samples[BENCH_ITERATION_COUNT / 2];
        g_detailed_results[idx].dma_p99 = samples[(BENCH_ITERATION_COUNT * 99) / 100];
        g_detailed_results[idx].dma_cpb = (float)g_detailed_results[idx].dma_med / (float)payload_len;
    }

    // Друк форматованої підсумкової таблиці
    printf("+------------+---------------------------------+---------------------------------+---------------------------------+\n");
    printf("| Розмір (B) |        POLLING (CPU Wait)       |     INTERRUPTS (SPSC FIFO)      |         CIRCULAR DMA (AHB)      |\n");
    printf("|            |  Min/Med/P99 (Cyc) |   CPB (C/B)|  Min/Med/P99 (Cyc) |   CPB (C/B)|  Min/Med/P99 (Cyc) |   CPB (C/B)|\n");
    printf("+------------+--------------------+------------+--------------------+------------+--------------------+------------+\n");

    for (size_t idx = 0; idx < TEST_ARRAY_SIZE; ++idx) {
        printf("| %10u | %5u/%5u/%5u | %10.2f | %5u/%5u/%5u | %10.2f | %5u/%5u/%5u | %10.2f |\n",
               (unsigned)g_detailed_results[idx].payload_size,
               (unsigned)g_detailed_results[idx].poll_min,
               (unsigned)g_detailed_results[idx].poll_med,
               (unsigned)g_detailed_results[idx].poll_p99,
               g_detailed_results[idx].poll_cpb,
               (unsigned)g_detailed_results[idx].irq_min,
               (unsigned)g_detailed_results[idx].irq_med,
               (unsigned)g_detailed_results[idx].irq_p99,
               g_detailed_results[idx].irq_cpb,
               (unsigned)g_detailed_results[idx].dma_min,
               (unsigned)g_detailed_results[idx].dma_med,
               (unsigned)g_detailed_results[idx].dma_p99,
               g_detailed_results[idx].dma_cpb);
    }
    printf("+------------+--------------------+------------+--------------------+------------+--------------------+------------+\n\n");
}

int main(void) {
    Benchmark_ExecuteFullSuite();
    return 0;
}
