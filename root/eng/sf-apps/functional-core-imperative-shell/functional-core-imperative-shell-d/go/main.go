// decide — чиста: (State, Input) Plan. Кожна горутина пише у СВІЙ індекс.
plans := make([]Plan, len(inputs))
var wg sync.WaitGroup
for i, inp := range inputs {
    wg.Add(1)
    go func(i int, inp Input) {          // state лише читається, спільного запису нема
        defer wg.Done()
        plans[i] = decide(state, inp)    // різні i → різні комірки → без мʼютекса
    }(i, inp)
}
wg.Wait()
