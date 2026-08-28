/* pcie_explorer.c — сканер PCIe пристроїв мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>

#define SYSFS_PCI_PATH "/sys/bus/pci/devices"

/* Структура стандартного заголовка PCI Header Type 0 (64 байти) */
typedef struct {
    uint16_t vendor_id;
    uint16_t device_id;
    uint16_t command;
    uint16_t status;
    uint8_t  revision_id;
    uint8_t  prog_if;
    uint8_t  subclass;
    uint8_t  class_code;
    uint8_t  cache_line_size;
    uint8_t  latency_timer;
    uint8_t  header_type;
    uint8_t  bist;
    uint32_t bar[6];
    uint32_t cardbus_cis;
    uint16_t sub_vendor_id;
    uint16_t sub_device_id;
    uint32_t rom_address;
    uint8_t  cap_pointer;
    uint8_t  reserved[7];
    uint8_t  interrupt_line;
    uint8_t  interrupt_pin;
    uint8_t  min_gnt;
    uint8_t  max_lat;
} __attribute__((packed)) pci_header_t;

/* Розшифровка Capabilities */
static void parse_capabilities(int fd, uint8_t cap_ptr) {
    uint8_t pos = cap_ptr & 0xFC;   /* два молодші біти зарезервовані */
    int guard = 48;                 /* запобіжник від зациклення списку */
    printf("    Capabilities list:");
    
    while (pos >= 0x40 && pos < 0xFF) {
        uint8_t cap_hdr[2];
        if (pread(fd, cap_hdr, 2, pos) != 2) break;
        
        uint8_t cap_id = cap_hdr[0];
        uint8_t next_ptr = cap_hdr[1];
        
        switch (cap_id) {
            case 0x01: printf(" [Power Management]"); break;
            case 0x05: printf(" [MSI]"); break;
            case 0x10: printf(" [PCI Express]"); break;
            case 0x11: printf(" [MSI-X]"); break;
            default:   printf(" [Cap ID 0x%02X]", cap_id); break;
        }
        pos = next_ptr;
    }
    printf("\n");
}

/* Обробка одного пристрою BDF */
static void inspect_device(const char *bdf) {
    char path[512];
    snprintf(path, sizeof(path), "%s/%s/config", SYSFS_PCI_PATH, bdf);
    
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        return;
    }
    
    pci_header_t hdr;
    if (read(fd, &hdr, sizeof(hdr)) != sizeof(hdr)) {
        close(fd);
        return;
    }
    
    printf("Пристрій [%s] — Vendor: 0x%04X, Device: 0x%04X (Class 0x%02X%02X)\n",
           bdf, hdr.vendor_id, hdr.device_id, hdr.class_code, hdr.subclass);
    
    /* Парсинг BARs */
    for (int i = 0; i < 6; i++) {
        uint32_t bar = hdr.bar[i];
        if (bar == 0) continue;
        
        if (bar & 0x01) {
            /* I/O BAR */
            printf("    BAR%d: Port I/O на 0x%04X\n", i, bar & ~0x03);
        } else {
            /* Memory BAR */
            int is_64bit = (bar & 0x06) == 0x04;
            int is_prefetchable = (bar & 0x08) != 0;
            uint64_t addr = bar & ~0x0F;
            
            if (is_64bit && i < 5) {
                uint64_t high = hdr.bar[i + 1];
                addr |= (high << 32);
                printf("    BAR%d (64-bit MMIO%s): 0x%016llX\n",
                       i, is_prefetchable ? ", Prefetchable" : "", (unsigned long long)addr);
                i++; /* Пропускаємо наступний BAR, бо він є старшою частиною */
            } else {
                printf("    BAR%d (32-bit MMIO%s): 0x%08X\n",
                       i, is_prefetchable ? ", Prefetchable" : "", bar & ~0x0F);
            }
        }
    }
    
    /* Перевірка прапора Status: Capabilities List */
    if (hdr.status & (1 << 4)) {
        parse_capabilities(fd, hdr.cap_pointer);
    }
    
    close(fd);
}

int main(void) {
    DIR *dir = opendir(SYSFS_PCI_PATH);
    if (!dir) {
        perror("Не вдалося відкрити sysfs pci path");
        return 1;
    }
    
    printf("=== PCI Express sysfs explorer (C implementation) ===\n");
    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') continue;
        inspect_device(entry->d_name);
    }
    
    closedir(dir);
    return 0;
}
