def sweep_efficiency():
    vin  = [12.0, 14.4, 16.8]            # сітка по входу
    iout = [0.1, 0.3, 1.0, 2.0, 3.0]     # сітка по навантаженню
    VOUT_NOM = 5.0

    port_send("CURR:PROT 4.0")           # ліміт струму БЖ за паспортом DUT — запобіжник
    port_send("FUNC CURR")               # навантаження в режим стабілізації струму (CC)
    print("Vin\tIout\tVout\teta%")

    for r, v in enumerate(vin):
        order = reversed(iout) if r & 1 else iout   # парний рядок — у зворотному порядку
        for i_set in order:
            eta = measure_point(v, i_set, VOUT_NOM)

            if eta < 0.0:
                print(f"# {v:.1f} V @ {i_set:.2f} A: DUT поза нормою")
                continue
            print(f"{v:.1f}\t{i_set:.2f}\t{VOUT_NOM:.3f}\t{eta:.1f}")
        port_send("INP OFF")             # розвантажити DUT між рядками Vвх

    port_send("OUTP OFF"); port_send("INP OFF")   # безпечне завершення
