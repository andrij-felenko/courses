#include "bsp/status.h"

const char *bsp_status_str(bsp_status_t status)
{
    switch (status) {
    case BSP_STATUS_OK:                return "OK";
    case BSP_STATUS_ERR_INVALID_PARAM: return "invalid parameter";
    case BSP_STATUS_ERR_NOT_INIT:      return "subsystem not initialized";
    case BSP_STATUS_ERR_BUSY:          return "hardware bus busy";
    case BSP_STATUS_ERR_TIMEOUT:       return "hardware timeout";
    case BSP_STATUS_ERR_BUS_FAULT:     return "bus transaction fault";
    case BSP_STATUS_ERR_POWER_FAULT:   return "power rail fault";
    case BSP_STATUS_ERR_UNSUPPORTED:   return "operation unsupported";
    default:                           break;
    }
    /* Невідомий код теж мусить логуватися, а не валити застосунок. */
    return "unknown status";
}
