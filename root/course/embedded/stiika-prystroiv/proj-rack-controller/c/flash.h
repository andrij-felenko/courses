/* Виклик OpenOCD на налагоджувачі конкретного слота. */
#ifndef RACK_FLASH_H
#define RACK_FLASH_H

#include "rack.h"

/* Прошити образ, звірити й пустити плату. Плата має бути під живленням. */
rack_status_t rack_flash_program(int slot_id, const char *image_path);

/* Повне стирання кристала. Викликається, коли плата вже стартувала
   з фабричного ROM-завантажувача (BOOT0 = 1). */
rack_status_t rack_flash_mass_erase(int slot_id);

#endif /* RACK_FLASH_H */
