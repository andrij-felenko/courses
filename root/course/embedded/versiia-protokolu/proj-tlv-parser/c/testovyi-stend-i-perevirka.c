int main(void) {
    TelemetryData_t data;
    
    /* 1. Базовий пакет v1.0 */
    const uint8_t pkt_v1[] = {
        0x01, 0x02, 0xE4, 0x0C,             /* Tag 1, Len 2: Voltage = 3300 mV */
        0x02, 0x04, 0x96, 0x00, 0x00, 0x00  /* Tag 2, Len 4: Current = 150 mA */
    };
    
    if (telemetry_parse_tlv_stream(pkt_v1, sizeof(pkt_v1), &data) == TLV_OK) {
        printf("Pkt v1 parsed: V=%u mV, I=%ld mA, Temp_present=%d, Unknown=%u\n",
               data.voltage_mv, (long)data.current_ma, 
               data.flags.has_temperature, data.unknown_tags_count);
    }
    
    /* 2. Розширений пакет із невідомим тегом 0x85 */
    const uint8_t pkt_v2[] = {
        0x01, 0x02, 0xE4, 0x0C,                         /* Voltage = 3300 mV */
        0x85, 0x06, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, /* НЕВІДОМИЙ ТЕГ 0x85 */
        0x03, 0x02, 0x2C, 0x09,                         /* Temp = 2348 (23.48 C) */
        0x04, 0x06, 'N', 'o', 'd', 'e', '-', '7'        /* Name = "Node-7" */
    };
    
    if (telemetry_parse_tlv_stream(pkt_v2, sizeof(pkt_v2), &data) == TLV_OK) {
        printf("Pkt v2 parsed: V=%u mV, Temp=%.2f C, Name='%s', Unknown=%u\n",
               data.voltage_mv, (double)data.temperature_c_x100 / 100.0,
               data.device_name, data.unknown_tags_count);
    }
    
    /* 3. Пакет із вкладеним TLV (Network Config) */
    const uint8_t pkt_nested[] = {
        0x05, 0x0A,                                     /* Tag 5 (NetConfig), Len 10 */
        0x10, 0x04, 0xC0, 0xA8, 0x01, 0x64,             /* Subtag 0x10 (IP): 192.168.1.100 */
        0x11, 0x02, 0x90, 0x1F                          /* Subtag 0x11 (Port): 8080 (0x1F90) */
    };
    
    if (telemetry_parse_tlv_stream(pkt_nested, sizeof(pkt_nested), &data) == TLV_OK) {
        printf("Pkt nested: IP_present=%d, Port=%u\n", 
               data.net_cfg.has_ip, data.net_cfg.port);
    }
    
    /* 4. Зіпсований пакет із некоректною довжиною */
    const uint8_t pkt_corrupt[] = {
        0x01, 0x50, 0xE4, 0x0C /* Заявлена довжина 80 байтів при фактичних 2 */
    };
    
    TlvStatus_t status = telemetry_parse_tlv_stream(pkt_corrupt, sizeof(pkt_corrupt), &data);
    printf("Corrupt packet status: %d (Expected %d)\n", status, TLV_ERR_INVALID_LENGTH);
    
    return 0;
}
