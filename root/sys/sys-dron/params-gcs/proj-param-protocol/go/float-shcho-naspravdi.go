// Перетягнути значення в потрібне ціле за оголошеним типом:
func typedInt(p *ParamValue) int32 {
    switch p.ParamType {
    case mavParamTypeInt8, mavParamTypeInt16, mavParamTypeInt32,
        mavParamTypeUint8, mavParamTypeUint16, mavParamTypeUint32:
        return paramAsInt(p.ParamValue) // байти, не округлення
    default:
        return int32(math.Round(float64(p.ParamValue))) // справді float
    }
}
