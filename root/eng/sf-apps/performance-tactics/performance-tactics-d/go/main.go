// Пул із N горутин тягне спільний канал. Тепер водночас
// обробляється N запитів — чекання в черзі падає приблизно в N разів.
const workers = 4

func workerLoop(q <-chan Request, wg *sync.WaitGroup) {
    defer wg.Done()
    for req := range q { // безпечний забір із каналу
        handleRequest(req) // чотири такі йдуть ОДНОЧАСНО
    }
}

func serveAllParallel(q <-chan Request) {
    var wg sync.WaitGroup
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go workerLoop(q, &wg)
    }
    wg.Wait()
}
