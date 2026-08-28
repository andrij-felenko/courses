var clkPrev = false
var qFf     = false

// тригер: одна-єдина мить захоплення
func ffCapture(data, clk bool) {
    rising := clk && !clkPrev         // фронт саме зараз?
    if rising {
        qFf = data                    // взяли рівно те, що є на фронті
    }
    clkPrev = clk
    // після фронту data хоч як міняйся — qFf не зрушиться (стіна)
}
