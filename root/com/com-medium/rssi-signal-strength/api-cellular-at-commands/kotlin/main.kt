import android.telephony.CellInfoLte
import android.telephony.CellSignalStrengthLte
import android.telephony.TelephonyManager

fun processLteSignalInfo(cellInfo: CellInfoLte) {
    val lteSignal: CellSignalStrengthLte = cellInfo.cellSignalStrength

    val rsrpDbm: Int = lteSignal.rsrp     // Діапазон: -140..-44 dBm
    val rsrqDb: Int = lteSignal.rsrq       // Діапазон: -20..-3 dB
    val rssiDbm: Int = lteSignal.rssi     // Загальний RSSI у dBm
    val snrDb: Int = lteSignal.rssnr       // Відношення сигнал/шум (SNR)
    val level: Int = lteSignal.level       // 5-бальна оцінка статусу (0..4)

    println("Android Telephony -> RSRP: $rsrpDbm dBm, RSRQ: $rsrqDb dB, Level: $level/4")
}
