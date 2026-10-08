#include <stdio.h>
#include <stdlib.h>
#include "cam_sdk.h"

int main(void) {
    CAM_STATUS status;
    uint32_t device_count = 0;
    CAM_DEVICE_INFO dev_list[8];
    CAM_HANDLE h_camera = NULL;

    /* Ініціалізація системного середовища SDK */
    status = Cam_InitializeSystem();
    if (status != CAM_SUCCESS) {
        printf("Помилка ініціалізації SDK: %d\n", status);
        return -1;
    }

    /* Опитування шини та перелік доступних пристроїв */
    status = Cam_EnumerateDevices(dev_list, 8, &device_count);
    if (status != CAM_SUCCESS || device_count == 0) {
        printf("Камери не знайдено або помилка опитування: %d\n", status);
        Cam_ShutdownSystem();
        return -1;
    }

    /* Відкриття сесії взаємодії з першою знайденою камерою */
    status = Cam_OpenDevice(dev_list[0].szID, &h_camera);
    if (status == CAM_SUCCESS) {
        printf("З'єднання успішно встановлено з пристроєм: %s\n", dev_list[0].szModelName);

        /* Конфігурування параметрів транспортного каналу USB 3.0 / GigE */
        Cam_SetTransportParam(h_camera, CAM_PARAM_PACKET_SIZE, 9000);

        /* Коректне закриття сесії та звільнення хендла */
        Cam_CloseDevice(h_camera);
    }

    /* Деініціалізація ресурсів бібліотеки */
    Cam_ShutdownSystem();
    return 0;
}
