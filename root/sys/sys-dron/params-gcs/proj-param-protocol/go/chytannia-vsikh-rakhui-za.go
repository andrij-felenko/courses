const paramTimeoutMS = 1000 // тиша довша за це = потік завмер

type ParamDownload struct {
    Total    uint16     // param_count з першого пакета
    Have     uint16     // скільки вже маємо
    Names    [][16]byte // таблиця імен, розмір param_count
    Values   []float32
    Got      []bool     // Got[i] — чи прийшов параметр i
    LastRxMS uint32     // коли прийшов останній PARAM_VALUE
}

// Викликається на КОЖЕН вхідний PARAM_VALUE:
func (d *ParamDownload) OnParamValue(p *ParamValue) {
    if d.Total == 0 { // перший пакет задає розмір
        d.Total = p.ParamCount
        d.Names = make([][16]byte, d.Total)
        d.Values = make([]float32, d.Total)
        d.Got = make([]bool, d.Total)
    }
    i := p.ParamIndex
    if i < d.Total && !d.Got[i] { // дублікати ігноруємо
        d.Names[i] = p.ParamID
        d.Values[i] = p.ParamValue
        d.Got[i] = true
        d.Have++
    }
    d.LastRxMS = nowMS() // потік живий — зсуваємо таймер
}
