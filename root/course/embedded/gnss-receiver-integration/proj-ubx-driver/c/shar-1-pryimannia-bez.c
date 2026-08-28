// Кільцевий буфер прийому: перервання пише, головний цикл читає.
// Розмір — степінь двійки, щоб маскувати індекс дешевим &, а не %.
#define RX_RING  512
static volatile uint8_t rx_ring[RX_RING];
static volatile uint16_t rx_head;   // куди пише ISR
static uint16_t          rx_tail;   // звідки читає цикл (не volatile: чіпає лише цикл)

// Викликається з перервання UART на кожен прийнятий байт. МУСИТЬ бути коротким.
void gnss_uart_isr(uint8_t byte) {
    uint16_t next = (rx_head + 1) & (RX_RING - 1);
    if (next != rx_tail) {          // є місце?
        rx_ring[rx_head] = byte;
        rx_head = next;
    }
    // Кільце повне — байт відкидаємо. Це не катастрофа: наступний валідний
    // пакет пересинхронізує автомат. Гірше було б заблокуватися чи зациклитись.
}
