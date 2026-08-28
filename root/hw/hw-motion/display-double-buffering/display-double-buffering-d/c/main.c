static uint16_t fb[2][480][800];   // два кадри, RGB565 — у зовнішній SDRAM
static volatile int back = 1;      // індекс буфера, у який малюємо

void present(void) {
    int front = back;              // готовий кадр піде на показ
    back ^= 1;                     // наступний малюватимемо в інший

    // 1) нова адреса показу — у ТІНЬОВИЙ регістр шару 0 (ще не діє)
    LTDC_Layer1->CFBAR = (uint32_t)&fb[front][0][0];
    // 2) попросити перезавантаження тіні в робочі регістри У VBLANK
    LTDC->SRCR = LTDC_SRCR_VBR;    // vertical blanking reload
}
