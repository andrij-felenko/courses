// Адреси-поштарі: запис сюди зводить INT у сусіда, читання — гасить.
// Зазвичай це дві найвищі адреси DPRAM (по одній на напрям).
#define MBX_TO_B  (*(volatile uint8_t *)(DPRAM_BASE + 0x0FFF))  // A пише → перериває B
#define MBX_TO_A  (*(volatile uint8_t *)(DPRAM_BASE + 0x0FFE))  // B пише → перериває A

// Продюсер після вдалого mailbox_send «дзвонить» сусідові:
static inline void ring_doorbell_to_B(void)
{
    MBX_TO_B = 1;               // значення байдуже — важливий сам факт запису
}

// Обробник переривання на боці B: прокинувся, забрав ВСЕ, що встигло накопичитись.
void DPRAM_INT_Handler(void)
{
    uint8_t buf[PAYLOAD];
    int n;
    // Забираємо всі пакети, а не один: між дзвінками їх могло лягти кілька.
    while ((n = mailbox_recv(MB_A2B, &SEM_A2B, buf, sizeof buf)) > 0)
        process_packet(buf, (uint8_t)n);

    (void)MBX_TO_B;             // читаємо свою скриньку-поштар → гасимо INT
}
