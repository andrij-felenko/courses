#define ADC_MAX 4095                 // 12 біт

static int calMin = ADC_MAX;         // почати з протилежних країв, щоб перше ж
static int calMax = 0;               // виміряне значення їх «стягнуло» до правди

static int clampi(int v, int lo, int hi) { return v < lo ? lo : (v > hi ? hi : v); }

// Викликати в циклі протягом кількох секунд, поки крутиш ручку від упору до упору.
void calibrate_sweep(void) {
  int raw = potSample();
  if (raw < calMin) calMin = raw;
  if (raw > calMax) calMax = raw;
}

// Після калібрування: масштабувати від РЕАЛЬНИХ країв і затиснути в межі.
int pot_percent(void) {
  int raw = potSample();
  int pct = (raw - calMin) * 100 / (calMax - calMin);   // пропорція замість map()
  return clampi(pct, 0, 100);        // не вилазити за 0..100 через шум на краях
}
