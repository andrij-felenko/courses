// Рахунок за місяць для заданої кількості оплачуваних годин.
// hoursBilled — скільки годин реально тікає лічильник.
func monthlyCostUSD(pricePerHour, hoursBilled float64) float64 {
    return pricePerHour * hoursBilled // платимо лише за оплачувані години
}

// Скільки активних годин на місяць для сервісу «години на день × дні».
func activeHours(hoursPerDay, workdaysPerMonth float64) float64 {
    return hoursPerDay * workdaysPerMonth
}
