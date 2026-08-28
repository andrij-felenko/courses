func sweepEfficiency() {
	vin := []float64{12.0, 14.4, 16.8}           // сітка по входу
	iout := []float64{0.1, 0.3, 1.0, 2.0, 3.0}   // сітка по навантаженню
	const voutNom = 5.0

	portSend("CURR:PROT 4.0") // ліміт струму БЖ за паспортом DUT — запобіжник
	portSend("FUNC CURR")     // навантаження в режим стабілізації струму (CC)
	fmt.Println("Vin\tIout\tVout\teta%")

	for r, v := range vin {
		for k := range iout {
			idx := k
			if r&1 == 1 { // парний рядок — у зворотному порядку
				idx = len(iout) - 1 - k
			}
			iSet := iout[idx]
			eta := measurePoint(v, iSet, voutNom)

			if eta < 0.0 {
				fmt.Printf("# %.1f V @ %.2f A: DUT поза нормою\n", v, iSet)
				continue
			}
			fmt.Printf("%.1f\t%.2f\t%.3f\t%.1f\n", v, iSet, voutNom, eta)
		}
		portSend("INP OFF") // розвантажити DUT між рядками Vвх
	}
	portSend("OUTP OFF")
	portSend("INP OFF") // безпечне завершення
}
