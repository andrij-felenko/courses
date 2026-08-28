#include <stdint.h>
#include <stdbool.h>

/* C-сумісний процедурний інтерфейс для інтеграції з FFI та системними демонами */

typedef struct katran_handle katran_handle_t;

katran_handle_t* katran_create(void);
void katran_destroy(katran_handle_t *h);

bool katran_attach_interface(katran_handle_t *h, const char *ifname);
bool katran_detach_interface(katran_handle_t *h, const char *ifname);

bool katran_add_vip_raw(katran_handle_t *h, uint32_t vip, uint16_t port, uint8_t proto, uint32_t mode);
bool katran_remove_vip_raw(katran_handle_t *h, uint32_t vip, uint16_t port, uint8_t proto);

bool katran_add_backend_raw(katran_handle_t *h, uint32_t vip, uint16_t port, uint8_t proto,
                            uint32_t backend_ip, uint16_t backend_port, uint32_t weight);
bool katran_rebuild_maglev_table(katran_handle_t *h, uint32_t vip, uint16_t port, uint8_t proto);
