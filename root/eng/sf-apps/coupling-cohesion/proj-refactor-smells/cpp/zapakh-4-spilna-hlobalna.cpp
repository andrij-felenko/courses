// Спільне зчеплення: глобал, у який пише і читає будь-хто, будь-коли
volatile int  g_rssi        = 0;
volatile bool g_linkUp      = false;
uint32_t      g_packetsLost = 0;

// у перериванні радіо:
void radio_isr() { g_rssi = readRssi(); g_linkUp = (g_rssi > -90); }
// у задачі телеметрії:
void telemetryTask() { if (g_linkUp) send(g_rssi); }
// у веб-конфізі:
void onReset() { g_packetsLost = 0; g_linkUp = false; }  // хто ще це бачить?
