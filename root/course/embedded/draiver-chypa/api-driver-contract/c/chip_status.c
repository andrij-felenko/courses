#include "chip_status.h"

const char *chip_status_str(chip_status_t status)
{
    switch (status) {
    case CHIP_STATUS_OK:               return "OK";
    case CHIP_ERR_INVALID_PARAM:       return "INVALID_PARAM";
    case CHIP_ERR_COMM_FAIL:           return "COMM_FAIL";
    case CHIP_ERR_TIMEOUT:             return "TIMEOUT";
    case CHIP_ERR_DEVICE_NOT_FOUND:    return "DEVICE_NOT_FOUND";
    case CHIP_ERR_NOT_INITIALIZED:     return "NOT_INITIALIZED";
    case CHIP_ERR_DATA_NOT_READY:      return "DATA_NOT_READY";
    case CHIP_ERR_SELF_TEST_FAILED:    return "SELF_TEST_FAILED";
    case CHIP_ERR_CALIBRATION_INVALID: return "CALIBRATION_INVALID";
    default:                           return "UNKNOWN";
    }
}
