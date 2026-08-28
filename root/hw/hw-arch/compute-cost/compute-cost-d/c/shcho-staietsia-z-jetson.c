// Слідкувати за тротлінгом просто: міряй FPS вікнами по N кадрів,
// а не одноразово на старті — і ти побачиш просідання, коли чип нагріється.
#define WIN 30
static double acc = 0; static int n = 0;

void on_frame(double frame_ms) {
    acc += frame_ms; n++;
    if (n == WIN) {
        double fps = 1000.0 * WIN / acc;   // середній FPS за вікно
        printf("FPS(вікно): %.1f\n", fps); // падає з часом → почався тротлінг
        acc = 0; n = 0;
    }
}
