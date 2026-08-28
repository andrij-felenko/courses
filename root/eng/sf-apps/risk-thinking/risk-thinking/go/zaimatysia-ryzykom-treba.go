// РИЗИК ВШИТО: зовнішній виклик прямо в бізнес-логіці, без страховки
func chargeCustomer(customerID int, amount float64) float64 {
	// прямий синхронний виклик чужого сервісу — якщо він ляже, ляжемо ми
	resp, _ := http.PostForm("https://pay.example.com/charge",
		url.Values{"customer_id": {strconv.Itoa(customerID)},
			"amount": {fmt.Sprint(amount)}})
	body, _ := io.ReadAll(resp.Body) // а якщо таймаут? а якщо 500? а якщо повільно?
	v, _ := strconv.ParseFloat(string(body), 64)
	return v
}
