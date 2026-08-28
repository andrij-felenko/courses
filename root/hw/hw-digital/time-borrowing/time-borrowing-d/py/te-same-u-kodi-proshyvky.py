clk_prev = False
q_ff     = False

# тригер: одна-єдина мить захоплення
def ff_capture(data: bool, clk: bool) -> None:
    global clk_prev, q_ff
    rising = clk and not clk_prev     # фронт саме зараз?
    if rising:
        q_ff = data                   # взяли рівно те, що є на фронті
    clk_prev = clk
    # після фронту data хоч як міняйся — q_ff не зрушиться (стіна)
