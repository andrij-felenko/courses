// Наївно: надіслати, дочекатися, тоді надіслати наступний.
// Якщо система завмерла — ми просто НЕ шлемо проби, що мали б бути повільними.
for i := 0; i < n; i++ {
    t0 := time.Now()
    doRequest()                  // затик тут спиняє й сам вимірювальний цикл
    record(time.Since(t0))       // у вибірці лише те, що встигли надіслати
}

// Правильно: у проб є ГРАФІК. Затримку рахуємо від planned-часу,
// а не від миті, коли черга нарешті до неї дійшла.
interval := time.Second / time.Duration(rps)
start := time.Now()
for i := 0; i < n; i++ {
    planned := start.Add(time.Duration(i) * interval)
    doRequest()
    record(time.Since(planned))  // включає й час, що проба прочекала в затику
}
