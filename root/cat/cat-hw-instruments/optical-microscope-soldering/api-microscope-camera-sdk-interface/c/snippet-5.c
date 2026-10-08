#include <stdio.h>
#include <math.h>
#include "cam_sdk.h"

CAM_STATUS ConfigureSensorPipeline(CAM_HANDLE h_cam) {
    CAM_STATUS status;

    /* Встановлення тривалості експозиції 2500 мкс (2.5 мс) */
    status = Cam_SetParamFloat(h_cam, CAM_PARAM_EXPOSURE_TIME_US, 2500.0f);
    if (status != CAM_SUCCESS) return status;

    /* Налаштування аналогового підсилення сенсора (6.0 dB) */
    status = Cam_SetParamFloat(h_cam, CAM_PARAM_GAIN_DB, 6.0f);
    if (status != CAM_SUCCESS) return status;

    /* Встановлення області інтересу ROI: OffsetX=128, OffsetY=128, Width=1024, Height=768 */
    status = Cam_SetROI(h_cam, 128, 128, 1024, 768);
    if (status != CAM_SUCCESS) return status;

    /* Активація режиму апаратного суммування пікселів 2x2 Binning */
    status = Cam_SetParamEnum(h_cam, CAM_PARAM_BINNING_MODE, CAM_BINNING_SUM_2X2);
    if (status != CAM_SUCCESS) return status;

    /* Завантаження кривої контрастування LUT у пам'ять камери */
    uint16_t lut_table[4096];
    for (int i = 0; i < 4096; i++) {
        lut_table[i] = (uint16_t)(sqrt((double)i / 4095.0) * 4095.0);
    }
    status = Cam_WriteLUT(h_cam, 0, lut_table, 4096);
    
    return status;
}
