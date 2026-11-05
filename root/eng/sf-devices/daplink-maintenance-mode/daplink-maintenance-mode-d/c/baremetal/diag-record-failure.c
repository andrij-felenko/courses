#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define SCSI_SENSE_KEY_NO_SENSE         0x00U
#define SCSI_SENSE_KEY_MEDIUM_ERROR     0x03U
#define SCSI_SENSE_KEY_ILLEGAL_REQUEST  0x05U

#define SCSI_ASC_NO_ADDITIONAL_SENSE    0x00U
#define SCSI_ASC_WRITE_ERROR            0x0CU
#define SCSI_ASC_WRITE_PROTECTED        0x27U
#define SCSI_ASC_INVALID_FIELD_IN_CDB   0x24U

typedef enum {
    DIAG_OK = 0,
    DIAG_ERR_FLASH_TIMEOUT,
    DIAG_ERR_VERIFY_MISMATCH,
    DIAG_ERR_VECTOR_INVALID,
    DIAG_ERR_WRITE_PROTECTED
} diag_error_t;

typedef struct {
    diag_error_t error_code;
    uint32_t fault_address;
    uint32_t expected_data;
    uint32_t actual_data;
} diag_context_t;

static diag_context_t g_diag_ctx = {DIAG_OK, 0U, 0U, 0U};

// Фіксація помилки у глобальному контексті діагностики
void diag_record_failure(diag_error_t err, uint32_t addr, uint32_t exp, uint32_t act) {
    g_diag_ctx.error_code = err;
    g_diag_ctx.fault_address = addr;
    g_diag_ctx.expected_data = exp;
    g_diag_ctx.actual_data = act;
}

// Формування стандартної 18-байтової відповіді на запит SCSI REQUEST SENSE
uint32_t scsi_build_sense_response(uint8_t *response_buffer, uint32_t max_length) {
    if (max_length < 18U) {
        return 0U;
    }
    memset(response_buffer, 0, 18U);
    response_buffer[0] = 0x70U; // Фіксований дескриптор поточних помилок
    response_buffer[7] = 10U;   // Додаткова довжина даних чутливості

    switch (g_diag_ctx.error_code) {
        case DIAG_ERR_FLASH_TIMEOUT:
        case DIAG_ERR_VERIFY_MISMATCH:
            response_buffer[2] = SCSI_SENSE_KEY_MEDIUM_ERROR;
            response_buffer[12] = SCSI_ASC_WRITE_ERROR;
            response_buffer[13] = 0x00U;
            break;
        case DIAG_ERR_WRITE_PROTECTED:
            response_buffer[2] = SCSI_SENSE_KEY_ILLEGAL_REQUEST;
            response_buffer[12] = SCSI_ASC_WRITE_PROTECTED;
            response_buffer[13] = 0x00U;
            break;
        case DIAG_ERR_VECTOR_INVALID:
            response_buffer[2] = SCSI_SENSE_KEY_ILLEGAL_REQUEST;
            response_buffer[12] = SCSI_ASC_INVALID_FIELD_IN_CDB;
            response_buffer[13] = 0x00U;
            break;
        default:
            response_buffer[2] = SCSI_SENSE_KEY_NO_SENSE;
            response_buffer[12] = SCSI_ASC_NO_ADDITIONAL_SENSE;
            response_buffer[13] = 0x00U;
            break;
    }
    return 18U;
}

// Динамічний синтез сектора файлу FAIL.TXT для віртуальної файлової системи
void vfs_generate_fail_txt(uint8_t *lba_sector_buffer) {
    memset(lba_sector_buffer, ' ', 512U);
    char temp[256];
    const char *reason = "Unknown hardware failure.";

    switch (g_diag_ctx.error_code) {
        case DIAG_ERR_FLASH_TIMEOUT:
            reason = "Flash controller hardware timeout during erase/write.";
            break;
        case DIAG_ERR_VERIFY_MISMATCH:
            reason = "Flash verification mismatch. Memory cells failed to hold charge.";
            break;
        case DIAG_ERR_VECTOR_INVALID:
            reason = "Vector table is invalid. Initial MSP or Reset Handler out of range.";
            break;
        case DIAG_ERR_WRITE_PROTECTED:
            reason = "Target sector is write-protected or flash security lock active.";
            break;
        default:
            break;
    }

    int len = 0;
    // Формування текстового звіту у форматі ASCII
    const char header[] = "error: An error occurred during the update.

reason: ";
    memcpy(temp, header, strlen(header));
    len += (int)strlen(header);

    memcpy(temp + len, reason, strlen(reason));
    len += (int)strlen(reason);

    const char footer[] = "

type: interface-firmware-update

";
    memcpy(temp + len, footer, strlen(footer));
    len += (int)strlen(footer);

    memcpy(lba_sector_buffer, temp, (size_t)len);
}

// Фільтрація імен системних файлів операційних систем
bool vfs_is_valid_firmware_file(const char *filename_8_3) {
    if (filename_8_3[0] == '.' || filename_8_3[0] == 0x05 || filename_8_3[0] == (char)0xE5) {
        return false;
    }
    // Перевірка допустимих розширень BIN або HEX
    const char *ext = &filename_8_3[8];
    bool is_bin = (ext[0] == 'B' && ext[1] == 'I' && ext[2] == 'N');
    bool is_hex = (ext[0] == 'H' && ext[1] == 'E' && ext[2] == 'X');
    return (is_bin || is_hex);
}
