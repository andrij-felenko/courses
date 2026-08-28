int main(void) {
    fpv_system systems[] = {
        // АНАЛОГ: нема кодера/декодера; радіо стале (одне число → lo=hi).
        // Домінує сенсор камери; ~19 мс разом.
        { .name = "Аналог",
          .sensor  = {12, 12}, .encode = {0, 0},
          .radio   = { 2,  2}, .decode = {0, 0}, .display = {5, 5},
          .fps = 60 },

        // HDZERO: однобічний, фіксована затримка; кодек є, але без пересилань
        // радіо стале. ~14 мс при 100 к/с.
        { .name = "HDZero",
          .sensor  = {3, 3}, .encode = {4, 4},
          .radio   = {3, 3}, .decode = {2, 2}, .display = {2, 2},
          .fps = 100 },

        // DJI O4 (гоночний режим): двобічний, але в гонці радіо майже без
        // розкиду; ~15 мс скло-скло.
        { .name = "DJI O4 (race)",
          .sensor  = {3, 3}, .encode = {4, 5},
          .radio   = {2, 3}, .decode = {3, 3}, .display = {3, 3},
          .fps = 100 },

        // WALKSNAIL: двобічний; у полі ~22 мс, за бетоном ~35 мс через
        // пересилання — радіо тримає ШИРОКИЙ діапазон.
        { .name = "Walksnail",
          .sensor  = {4, 4}, .encode = {6, 7},
          .radio   = {6, 18}, .decode = {4, 4}, .display = {2, 2},
          .fps = 120 },
    };

    int n = sizeof(systems) / sizeof(systems[0]);
    float speed = 120.0f;   // км/год — типова гоночна

    for (int i = 0; i < n; i++)
        report(&systems[i], speed);

    return 0;
}
