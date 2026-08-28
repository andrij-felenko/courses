// Прив'язка структур до фізичних адрес DPRAM.
// A2B — скринька «застосунок → зв'язок»; B2A — назад.
// БАЗУ підставляє КОЖНЕ ядро свою (у ядра A і ядра B адреси різні,
// а зміщення полів усередині — однакові).
#define DPRAM_BASE   0x60000000u        // приклад: сюди мапнута DPRAM цього ядра

#define MB_A2B  ((mailbox_t volatile *)(DPRAM_BASE + 0x000))
#define MB_B2A  ((mailbox_t volatile *)(DPRAM_BASE + 0x100))

// Семафори — окремий простір, теж мапнутий у пам'ять.
// Латч 0 стереже скриньку A2B, латч 1 — B2A.
#define SEM_BASE  0x60010000u
#define SEM_A2B   (*(volatile uint8_t *)(SEM_BASE + 0))
#define SEM_B2A   (*(volatile uint8_t *)(SEM_BASE + 1))
