// Один крок логіки вікон: якщо зараз наше вікно і пакет влізає — передаємо.
static void run_slot_logic(uint64_t now) {
    frame_pos_t p = where_in_frame(now);

    if (g_slot_owner[p.slot] == MY_NODE_ID) {
        // наше вікно: передаємо, лише якщо пакет ще влізе до захисної зони
        uint32_t tx_us = packet_air_time_us(my_len);   // скільки летітиме наш пакет
        if (have_packet() && fits_in_slot(p.into_us, tx_us)) {
            radio_transmit(my_packet, my_len);
        } else {
            radio_listen();    // вже пізно в цьому вікні або нема що слати
        }
    } else {
        radio_listen();        // чуже або вільне вікно — мовчимо, слухаємо
    }
}
