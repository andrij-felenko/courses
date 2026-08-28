/* C Implementation: ACPI Table Inspector & AML Header Parser */
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

/* Валідація 8-бітної контрольної суми */
int validate_acpi_checksum(const uint8_t *buffer, size_t length) {
    if (!buffer || length == 0) return 0;
    uint8_t sum = 0;
    for (size_t i = 0; i < length; ++i) {
        sum += buffer[i];
    }
    return (sum == 0);
}

/* Простий аналіз AML PkgLength (довжини пакета) */
size_t parse_aml_pkg_length(const uint8_t *aml_data, size_t max_len, size_t *bytes_read) {
    if (max_len < 1) return 0;
    uint8_t lead = aml_data[0];
    uint8_t byte_count = (lead >> 6) & 0x03;

    if (byte_count == 0) {
        if (bytes_read) *bytes_read = 1;
        return (lead & 0x3F);
    }

    if (max_len < (size_t)(byte_count + 1)) return 0;
    size_t length = (lead & 0x0F);
    for (uint8_t i = 0; i < byte_count; ++i) {
        length |= ((size_t)aml_data[1 + i]) << (4 + i * 8);
    }
    if (bytes_read) *bytes_read = byte_count + 1;
    return length;
}

int process_acpi_table_file(const char *filepath) {
    FILE *f = fopen(filepath, "rb");
    if (!f) {
        perror("Failed to open ACPI table file");
        return 1;
    }

    struct acpi_table_header hdr;
    if (fread(&hdr, 1, sizeof(hdr), f) != sizeof(hdr)) {
        fprintf(stderr, "Failed to read ACPI header\n");
        fclose(f);
        return 1;
    }

    if (hdr.length < sizeof(struct acpi_table_header)) {
        fprintf(stderr, "Invalid header length field: %u\n", hdr.length);
        fclose(f);
        return 1;
    }

    uint8_t *full_table = (uint8_t *)malloc(hdr.length);
    if (!full_table) {
        fprintf(stderr, "Memory allocation failure for %u bytes\n", hdr.length);
        fclose(f);
        return 1;
    }

    fseek(f, 0, SEEK_SET);
    size_t read_bytes = fread(full_table, 1, hdr.length, f);
    fclose(f);

    if (read_bytes != hdr.length) {
        fprintf(stderr, "Read mismatch: expected %u, got %zu\n", hdr.length, read_bytes);
        free(full_table);
        return 1;
    }

    int valid_sum = validate_acpi_checksum(full_table, hdr.length);

    printf("=== ACPI Table Metadata ===\n");
    printf("Signature:       %.4s\n", hdr.signature);
    printf("Table Length:    %u bytes\n", hdr.length);
    printf("Revision:        %u\n", hdr.revision);
    printf("OEM ID:          %.6s\n", hdr.oem_id);
    printf("OEM Table ID:    %.8s\n", hdr.oem_table_id);
    printf("ASL Compiler ID: %.4s\n", hdr.asl_compiler_id);
    printf("Checksum Status: %s\n", valid_sum ? "VALID (0x00)" : "INVALID");

    /* Якщо це DSDT або SSDT, показуємо інформацію про AML payload */
    if (memcmp(hdr.signature, "DSDT", 4) == 0 || memcmp(hdr.signature, "SSDT", 4) == 0) {
        size_t payload_offset = sizeof(struct acpi_table_header);
        if (hdr.length > payload_offset) {
            size_t aml_len = hdr.length - payload_offset;
            printf("AML Payload Size: %zu bytes\n", aml_len);
            
            size_t pkg_bytes_read = 0;
            size_t root_pkg_len = parse_aml_pkg_length(full_table + payload_offset, aml_len, &pkg_bytes_read);
            printf("Root AML PkgLength: %zu bytes (encoded in %zu header bytes)\n", root_pkg_len, pkg_bytes_read);
        }
    }

    free(full_table);
    return valid_sum ? 0 : 2;
}

int main(int argc, char **argv) {
    const char *path = (argc > 1) ? argv[1] : "/sys/firmware/acpi/tables/FADT";
    return process_acpi_table_file(path);
}
