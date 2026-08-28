/* Змінна, спільна між головним циклом та обробником переривання */
volatile uint32_t g_packet_counter = 0;
volatile uint32_t g_device_flags = 0;

void process_data(void) {
    /* Наївний інкремент у фоновому потоці */
    g_packet_counter++;
    
    /* Наївне встановлення бітового прапорця */
    g_device_flags |= (1U << 3);
}
