import "math"

// Груповий час із масиву виміряних фаз phi[k] на сітці частот із кроком df (Гц).
// phi — у радіанах; результат tau[k] — у секундах. N точок.
// τг = −dφ/dω = −(Δφ) / (2π·Δf)  — центральна різниця між сусідами.
func groupDelayFromPhase(phi []float64, df float64) []float64 {
    N := len(phi)
    twoPiDf := 2.0 * math.Pi * df
    tau := make([]float64, N)
    for k := 1; k < N-1; k++ {
        dphi := phi[k+1] - phi[k-1]         // різниця через дві точки (апертура 2·df)
        // розгортання стрибка ±2π, якщо фаза «перескочила» межу:
        if dphi >  math.Pi { dphi -= 2.0 * math.Pi }
        if dphi < -math.Pi { dphi += 2.0 * math.Pi }
        tau[k] = -dphi / (2.0 * twoPiDf)    // ділимо на 2·(2π·df): центральна різниця
    }
    tau[0] = tau[1]                         // краї — копією сусіда
    tau[N-1] = tau[N-2]
    return tau
}
