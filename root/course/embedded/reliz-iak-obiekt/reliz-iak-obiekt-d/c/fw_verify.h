#ifndef FW_VERIFY_H
#define FW_VERIFY_H

#include "fw_header.h"

/* Повна перевірка релізу перед передачею керування.
   hdr — дескриптор, відображений у Flash;
   payload_addr — адреса тіла образу (перевіряється проти load_address). */
fw_verify_t fw_verify_release(const fw_header_t *hdr, uint32_t payload_addr);

/* Символьне ім'я коду відмови — те саме, яким воно виходить у діагностичний
   протокол і в журнал сервера оновлень. */
const char *fw_verify_message(fw_verify_t code);

#endif /* FW_VERIFY_H */
