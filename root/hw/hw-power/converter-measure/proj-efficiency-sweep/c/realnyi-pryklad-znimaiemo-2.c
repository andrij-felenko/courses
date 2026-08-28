void sweep_efficiency(void)
{
    const float vin[]  = { 12.0f, 14.4f, 16.8f };          // сітка по входу
    const float iout[] = { 0.1f, 0.3f, 1.0f, 2.0f, 3.0f }; // сітка по навантаженню
    const int   NV = 3, NI = 5;
    const float VOUT_NOM = 5.0f;

    port_send("CURR:PROT 4.0");        // ліміт струму БЖ за паспортом DUT — запобіжник
    port_send("FUNC CURR");            // навантаження в режим стабілізації струму (CC)
    printf("Vin\tIout\tVout\teta%%\n");

    for (int r = 0; r < NV; r++) {
        for (int k = 0; k < NI; k++) {
            int idx = (r & 1) ? (NI - 1 - k) : k;   // парний рядок — у зворотному порядку
            float i_set = iout[idx];
            float eta = measure_point(vin[r], i_set, VOUT_NOM);

            if (eta < 0.0f) { printf("# %.1f V @ %.2f A: DUT поза нормою\n", vin[r], i_set); continue; }
            printf("%.1f\t%.2f\t%.3f\t%.1f\n", vin[r], i_set, VOUT_NOM, eta);
        }
        port_send("INP OFF");          // розвантажити DUT між рядками Vвх
    }
    port_send("OUTP OFF"); port_send("INP OFF");   // безпечне завершення
}
