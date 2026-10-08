#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cam_sdk.h"

/* Зворотна функція обробки кадрів у потоці DMA */
void CAM_CALL FrameCallback(CAM_FRAME_BUFFER* pBuffer, void* pUserContext) {
    if (pBuffer->eStatus == CAM_FRAME_COMPLETED) {
        /* Масив для обробленого колірного зображення RGB24 */
        uint8_t* pRGB24 = (uint8_t*)malloc(pBuffer->nWidth * pBuffer->nHeight * 3);

        /* Дезабайєризація сирого масиву RAW12/RAW8 у RGB24 */
        Cam_ConvertRawToRGB24(pBuffer->pData, pRGB24, pBuffer->nWidth, pBuffer->nHeight, CAM_PIXEL_BAYER_RG8);

        /* Програмне накладання вимірювальної калібрувальної сітки (Grid Overlay) */
        Cam_ApplyMeasurementGridOverlay(pRGB24, pBuffer->nWidth, pBuffer->nHeight, 50 /* крок сітки в пікселях */);

        /* Збереження результату у форматі JPEG */
        Cam_SaveBufferToJPEG("inspection_frame.jpg", pRGB24, pBuffer->nWidth, pBuffer->nHeight, 90);

        free(pRGB24);
    }
    /* Повернення буфера у кільцеву чергу драйвера */
    Cam_QueueBuffer(pBuffer->hCamera, pBuffer);
}

void StartContinuousGrabbing(CAM_HANDLE h_cam) {
    /* Реєстрація функції зворотного виклику */
    Cam_RegisterFrameCallback(h_cam, FrameCallback, NULL);
    /* Запуск потоку захоплення */
    Cam_StartAcquisition(h_cam);
}
