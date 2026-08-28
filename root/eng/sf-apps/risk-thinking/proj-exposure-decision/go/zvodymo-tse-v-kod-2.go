// Варіант архітектури: назва + список його ризиків.
type Variant struct {
	Name  string
	Risks []Risk
}

// Сумарна експозиція варіанта — сума експозицій усіх ризиків (НАЇВНА версія).
func totalExposureNaive(v Variant) float64 {
	sum := 0.0
	for _, r := range v.Risks {
		sum += exposure(r)
	}
	return sum
}
