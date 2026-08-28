#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>

/* Тип адресації за стандартом IEEE 802 */
typedef enum {
    MAC_TYPE_UNIVERSAL_UNICAST   = 0,
    MAC_TYPE_UNIVERSAL_MULTICAST = 1,
    MAC_TYPE_LOCAL_UNICAST       = 2,
    MAC_TYPE_LOCAL_MULTICAST     = 3
} mac_address_type_t;

/* Структура розібраної MAC-адреси */
typedef struct {
    uint8_t raw[6];
    uint32_t oui_24;        /* Старші 24 біти (MA-L) */
    mac_address_type_t type;
    bool is_valid;
} parsed_mac_t;

/* Структура дескриптора пристрою USB (USB 2.0) */
typedef struct {
    uint16_t bcd_usb;
    uint8_t  device_class;
    uint8_t  device_subclass;
    uint8_t  device_protocol;
    uint8_t  max_packet_size0;
    uint16_t vendor_id;
    uint16_t product_id;
    uint16_t bcd_device;
    bool     is_valid;
} parsed_usb_device_t;

/* Допоміжна функція перетворення символу hex у 4-бітне число */
static int hex_char_to_nibble(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

/* Парсинг рядка MAC-адреси (підтримує роздільники ':', '-' або без них) */
bool parse_mac_string(const char *str, parsed_mac_t *out_mac) {
    if (!str || !out_mac) return false;
    memset(out_mac, 0, sizeof(parsed_mac_t));

    uint8_t bytes[6] = {0};
    int byte_idx = 0;
    int nibble_cnt = 0;
    uint8_t cur_byte = 0;

    for (size_t i = 0; str[i] != '\0' && byte_idx < 6; ++i) {
        char c = str[i];
        if (c == ':' || c == '-') {
            if (nibble_cnt != 2) return false;
            bytes[byte_idx++] = cur_byte;
            cur_byte = 0;
            nibble_cnt = 0;
            continue;
        }
        int nibble = hex_char_to_nibble(c);
        if (nibble < 0) return false;

        cur_byte = (uint8_t)((cur_byte << 4) | (uint8_t)nibble);
        nibble_cnt++;
        if (nibble_cnt == 2) {
            bytes[byte_idx++] = cur_byte;
            cur_byte = 0;
            nibble_cnt = 0;
        }
    }

    if (byte_idx != 6 || nibble_cnt != 0) return false;

    memcpy(out_mac->raw, bytes, 6);
    out_mac->oui_24 = ((uint32_t)bytes[0] << 16) | ((uint32_t)bytes[1] << 8) | (uint32_t)bytes[2];

    bool is_group = (bytes[0] & 0x01) != 0;
    bool is_local = (bytes[0] & 0x02) != 0;

    if (!is_group && !is_local) out_mac->type = MAC_TYPE_UNIVERSAL_UNICAST;
    else if (is_group && !is_local) out_mac->type = MAC_TYPE_UNIVERSAL_MULTICAST;
    else if (!is_group && is_local) out_mac->type = MAC_TYPE_LOCAL_UNICAST;
    else out_mac->type = MAC_TYPE_LOCAL_MULTICAST;

    out_mac->is_valid = true;
    return true;
}

/* Перетворення EUI-48 у розширений 64-бітний формат EUI-64 (Zigbee / IPv6) */
void mac_to_eui64(const parsed_mac_t *mac, uint8_t out_eui64[8]) {
    if (!mac || !out_eui64) return;
    out_eui64[0] = mac->raw[0];
    out_eui64[1] = mac->raw[1];
    out_eui64[2] = mac->raw[2];
    out_eui64[3] = 0xFF;
    out_eui64[4] = 0xFE;
    out_eui64[5] = mac->raw[3];
    out_eui64[6] = mac->raw[4];
    out_eui64[7] = mac->raw[5];
}

/* Парсинг сирого 18-байтного USB Device Descriptor */
bool parse_usb_descriptor(const uint8_t *buffer, size_t len, parsed_usb_device_t *out_usb) {
    if (!buffer || len < 18 || !out_usb) return false;
    memset(out_usb, 0, sizeof(parsed_usb_device_t));

    uint8_t b_length = buffer[0];
    uint8_t b_descriptor_type = buffer[1];

    /* Інваріанти стандарту USB */
    if (b_length != 18 || b_descriptor_type != 0x01) return false;

    out_usb->bcd_usb = (uint16_t)(buffer[2] | ((uint16_t)buffer[3] << 8));
    out_usb->device_class = buffer[4];
    out_usb->device_subclass = buffer[5];
    out_usb->device_protocol = buffer[6];
    out_usb->max_packet_size0 = buffer[7];
    out_usb->vendor_id = (uint16_t)(buffer[8] | ((uint16_t)buffer[9] << 8));
    out_usb->product_id = (uint16_t)(buffer[10] | ((uint16_t)buffer[11] << 8));
    out_usb->bcd_device = (uint16_t)(buffer[12] | ((uint16_t)buffer[13] << 8));

    /* Валідація Vendor ID: не нуль і не зарезервований 0xFFFF */
    if (out_usb->vendor_id == 0x0000 || out_usb->vendor_id == 0xFFFF) {
        out_usb->is_valid = false;
        return false;
    }

    out_usb->is_valid = true;
    return true;
}

/* Генерація правила udev для Linux */
void generate_udev_rule(const parsed_usb_device_t *usb, const char *symlink_name, char *out_rule, size_t max_len) {
    if (!usb || !symlink_name || !out_rule || max_len == 0) return;
    snprintf(out_rule, max_len,
             "SUBSYSTEM==\"usb\", ATTR{idVendor}==\"%04x\", ATTR{idProduct}==\"%04x\", "
             "MODE=\"0666\", SYMLINK+=\"%s\"",
             usb->vendor_id, usb->product_id, symlink_name);
}
