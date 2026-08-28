static uint16_t fb[2][480][800];   // два кадри, 16 біт/піксель — у SDRAM
static volatile int back = 1;      // у який зараз малюємо

void swap_buffers(void) {
    int front = back;              // готовий кадр стане переднім
    back ^= 1;                     // малюватимемо в інший

    // нова адреса показу — у тіньовий регістр шару 0
    LTDC_Layer1->CFBAR = (uint32_t)&fb[front][0][0];
    // перезавантажити тіньові регістри САМЕ у вертикальному гасінні
    LTDC->SRCR = LTDC_SRCR_VBR;    // vertical blanking reload
}
