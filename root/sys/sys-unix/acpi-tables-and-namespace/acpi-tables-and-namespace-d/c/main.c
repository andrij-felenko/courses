/* C Implementation: Reading and Parsing FADT Table Header from sysfs */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#pragma pack(push, 1)
struct acpi_table_header {
    char     signature[4];
    uint32_t length;
    uint8_t  revision;
    uint8_t  checksum;
    char     oem_id[6];
    char     oem_table_id[8];
    uint32_t oem_revision;
    char     asl_compiler_id[4];
    uint32_t asl_compiler_revision;
};
#pragma pack(pop)

int check_acpi_checksum(const uint8_t *buffer, size_t length) {
    uint8_t sum = 0;
    for (size_t i = 0; i < length; ++i) {
        sum += buffer[i];
    }
    return sum == 0;
}

int inspect_fadt_table(const char *sysfs_path) {
    FILE *f = fopen(sysfs_path, "rb");
    if (!f) {
        perror("Failed to open ACPI table file");
        return -1;
    }

    struct acpi_table_header header;
    if (fread(&header, 1, sizeof(header), f) != sizeof(header)) {
        fprintf(stderr, "Truncated ACPI header read\n");
        fclose(f);
        return -1;
    }

    uint8_t *full_table = (uint8_t *)malloc(header.length);
    if (!full_table) {
        fclose(f);
        return -1;
    }

    fseek(f, 0, SEEK_SET);
    if (fread(full_table, 1, header.length, f) != header.length) {
        fprintf(stderr, "Failed to read complete table body\n");
        free(full_table);
        fclose(f);
        return -1;
    }
    fclose(f);

    printf("ACPI Table Signature: %.4s\n", header.signature);
    printf("Total Size:           %u bytes\n", header.length);
    printf("OEM Identity:         %.6s\n", header.oem_id);
    printf("Checksum Status:      %s\n", 
           check_acpi_checksum(full_table, header.length) ? "VALID" : "CORRUPTED");

    free(full_table);
    return 0;
}
