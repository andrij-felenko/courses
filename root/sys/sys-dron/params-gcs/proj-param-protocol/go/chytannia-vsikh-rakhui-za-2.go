// Викликається періодично, поки список неповний:
func (d *ParamDownload) Tick() {
    if d.Total == 0 { // ще не почали
        return
    }
    if d.Have >= d.Total {
        d.onDownloadDone()
        return
    }
    if nowMS()-d.LastRxMS < paramTimeoutMS { // ще йдуть
        return
    }

    // потік завмер, але маємо не все — перепитуємо діри по одній
    for i := uint16(0); i < d.Total; i++ {
        if !d.Got[i] {
            sendParamRequestRead(i)
        }
    }
    d.LastRxMS = nowMS() // дамо їм час відповісти
}
