#include <stdint.h>

#define N_SLOTS    8        // вікон у кадрі
#define SLOT_US    1250     // тривалість одного вікна, мкс
#define MY_SLOT    3        // це вікно — наше

// Викликається з таймера щоразу на початку нового вікна.
// slot — номер поточного вікна в кадрі (0..N_SLOTS-1).
void on_slot_tick(uint8_t slot) {
    if (slot == MY_SLOT) {
        radio_transmit(my_packet, my_len);   // наша мить — говоримо
    } else {
        radio_listen();                       // чужа мить — слухаємо
    }
}
