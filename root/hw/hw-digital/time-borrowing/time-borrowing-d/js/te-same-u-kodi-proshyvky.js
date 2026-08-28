let clkPrev = false;
let qFf      = false;

// тригер: одна-єдина мить захоплення
function ffCapture(data, clk) {
    const rising = clk && !clkPrev;   // фронт саме зараз?
    if (rising) {
        qFf = data;                   // взяли рівно те, що є на фронті
    }
    clkPrev = clk;
    // після фронту data хоч як міняйся — qFf не зрушиться (стіна)
}
