const (
    setTimeoutMS = 1000
    setRetries   = 3
)

func paramSetBlocking(id []byte, want float32, typ uint8) bool {
    for attempt := 0; attempt < setRetries; attempt++ {
        sendParamSet(id, want, typ)
        t0 := nowMS()
        for nowMS()-t0 < setTimeoutMS {
            if pv, ok := recvParamValue(); ok && nameEq(pv.ParamID[:], id) {
                return floatEq(pv.ParamValue, want) // борт підтвердив САМЕ це
            }
        }
        // тиша → пакет загубився, шлемо PARAM_SET ще раз
    }
    return false // борт так і не підтвердив — не вважаємо записаним
}
