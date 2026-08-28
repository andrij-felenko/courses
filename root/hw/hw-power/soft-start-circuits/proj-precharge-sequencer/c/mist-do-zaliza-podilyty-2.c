// ── Межа із залізом (реалізуй під свою плату) ─────────────────────────
extern void     hw_relay_precharge(bool on); // котушка передзарядного реле Kпз
extern void     hw_relay_main(bool on);      // котушка головного контактора Kгол
extern uint16_t hw_adc_read_bus(void);       // сира вибірка АЦП із каналу шини
extern uint32_t hw_millis(void);             // монотонний час, мс
extern void     hw_fault_report(uint8_t code);

// Сирий код АЦП -> мілівольти на шині (через дільник).
static uint32_t adc_to_bus_mV(uint16_t raw)
{
    // Uадц = raw·Vref/FS ;  Uшини = Uадц·(Rв+Rн)/Rн
    uint32_t uadc_mV = (uint32_t)((uint64_t)raw * ADC_VREF_mV / ADC_FULLSCALE);
    uint64_t ubus    = (uint64_t)uadc_mV * (DIV_RTOP_ohm + DIV_RBOT_ohm) / DIV_RBOT_ohm;
    return (uint32_t)ubus;
}
