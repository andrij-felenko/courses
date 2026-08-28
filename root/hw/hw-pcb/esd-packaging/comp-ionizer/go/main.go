// поле впало під безпечний поріг? (12-біт АЦП, 0.806 мВ/крок)
const (
    adcThreshold = 124                 // ≈ 100 В на поверхні
    settle       = 300 * time.Millisecond // підряд триматись нижче порогу
)

func surfaceIsSafe() bool {
    var below time.Duration
    for below < settle {
        if adcRead(fieldSensor) < adcThreshold {
            below += 10 * time.Millisecond // ще 10 мс «чисто»
        } else {
            below = 0                      // підскочило — лік спочатку
        }
        time.Sleep(10 * time.Millisecond)
    }
    return true // тримається нижче порогу → нейтралізовано
}
