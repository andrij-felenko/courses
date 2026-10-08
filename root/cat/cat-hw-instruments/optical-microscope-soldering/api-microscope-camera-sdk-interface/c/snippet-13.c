#include <stdio.h>
#include <stdbool.h>
#include <windows.h>
#include "cam_sdk.h"

/* Потік-сторож для моніторингу та автоматичного відновлення з'єднання */
DWORD WINAPI CameraWatchdogThread(LPVOID lpParam) {
    CAM_HANDLE* phCamera = (CAM_HANDLE*)lpParam;
    
    while (1) {
        Sleep(1000); // Перевірка кожну секунду
        
        if (*phCamera != NULL) {
            CAM_STATUS status = Cam_CheckHeartbeat(*phCamera);
            if (status == CAM_ERR_DEVICE_LOST || status == CAM_ERR_TIMEOUT) {
                printf("Виявлено втрату зв'язку з камерою! Автоматичне відновлення...\n");
                
                Cam_CloseDevice(*phCamera);
                *phCamera = NULL;
                
                /* Цикл реініціалізації */
                while (1) {
                    uint32_t count = 0;
                    CAM_DEVICE_INFO dev_list[1];
                    if (Cam_EnumerateDevices(dev_list, 1, &count) == CAM_SUCCESS && count > 0) {
                        if (Cam_OpenDevice(dev_list[0].szID, phCamera) == CAM_SUCCESS) {
                            printf("Зв'язок з камерою успішно відновлено!\n");
                            /* Повторне завантаження витримки та ROI */
                            Cam_SetParamFloat(*phCamera, CAM_PARAM_EXPOSURE_TIME_US, 2500.0f);
                            Cam_StartAcquisition(*phCamera);
                            break;
                        }
                    }
                    Sleep(2000);
                }
            }
        }
    }
    return 0;
}
