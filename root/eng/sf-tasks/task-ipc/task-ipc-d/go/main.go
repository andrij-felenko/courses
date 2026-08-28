q := make(chan int)     // черга відліків давача
var busMutex sync.Mutex // замок на спільну шину дисплея

func taskSensor() { // ВИРОБНИК
    for {
        v := readSensor()
        q <- v // безпечно передали відлік (копія)
        time.Sleep(100 * time.Millisecond)
    }
}

func taskLog() { // СПОЖИВАЧ
    for {
        v := <-q          // чекаємо й беремо (блок)
        busMutex.Lock()   // ← зайняли спільну шину
        writeToDisplay(v) //   працюємо з нею
        busMutex.Unlock() // ← звільнили шину
    }
}
