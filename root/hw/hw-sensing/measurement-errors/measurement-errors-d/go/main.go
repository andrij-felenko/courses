// Калібрувальна поправка офсету (виміряна на нульовому вході — еталоні).
const (
    adcOffset  = 8  // систематичний зсув, віднімаємо ОДИН раз
    adcSamples = 16 // усереднення: гасить випадковий шум у √16 = 4 рази
)

func readADCCorrected() uint16 {
    var acc uint32
    for i := 0; i < adcSamples; i++ {
        acc += uint32(adcReadRaw()) // 16 сирих вибірок поспіль
    }
    avg := uint16(acc / adcSamples) // середнє → розкид ±3 стиснувся до ≈ ±0.75

    // систематичний зсув НЕ гаситься усередненням — віднімаємо окремо:
    if avg > adcOffset {
        return avg - adcOffset
    }
    return 0
}
