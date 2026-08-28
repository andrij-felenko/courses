// Зважене поєднання двох оцінок у форматі Q8.8.
// wGW — вага сірого світу в Q8.8 (0..256); вага білої плями = 256 - wGW.
static uint16_t blend(uint16_t a, uint16_t b, uint16_t wGW) {
    uint16_t wWP = ONE - wGW;
    uint32_t mix = (uint32_t)a * wGW + (uint32_t)b * wWP;
    return (uint16_t)(mix >> Q);              // назад у Q8.8
}

// Оцінити коефіцієнти обома методами й поєднати за довірою до сірого світу.
void estimate_awb(const RGB *img, int n,
                  uint16_t *gR, uint16_t *gG, uint16_t *gB) {
    uint16_t gwR, gwG, gwB, wpR, wpG, wpB;
    estimate_gray_world(img, n, &gwR, &gwG, &gwB);
    estimate_white_patch(img, n, &wpR, &wpG, &wpB);

    // Довіра до сірого світу = наскільки сцена різнобарвна.
    // Коефіцієнти сірого світу самі кажуть про перекіс: якщо gwR і gwB далеко
    // від 1.0 (ONE), сцена сильно кольорова → сірому світу віри менше.
    uint32_t devR = (gwR > ONE) ? (gwR - ONE) : (ONE - gwR);
    uint32_t devB = (gwB > ONE) ? (gwB - ONE) : (ONE - gwB);
    uint32_t dev  = (devR > devB) ? devR : devB;   // найгірший перекіс

    // Перекіс до ~половини (dev≈128 у Q8.8) уже вважаємо «дуже кольоровою» сценою.
    // wGW спадає від ONE (сіра сцена) до ~ONE/4 (сильний перекіс).
    uint16_t wGW;
    if (dev >= 128) wGW = ONE / 4;
    else            wGW = ONE - (uint16_t)((dev * (ONE - ONE / 4)) / 128);

    *gR = blend(gwR, wpR, wGW);
    *gG = ONE;                                 // опорний канал завжди 1.0
    *gB = blend(gwB, wpB, wGW);
}
