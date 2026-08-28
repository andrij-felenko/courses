# Однорозрядний повний суматор двома мультиплексорами 8→1,
# що адресуються тими самими трьома бітами (a — старший, cin — молодший).
#            abc: 000 001 010 011 100 101 110 111
LUT_SUM  = [    0,  1,  1,  0,  1,  0,  0,  1 ]   # = XOR3
LUT_COUT = [    0,  0,  0,  1,  0,  1,  1,  1 ]   # = MAJ3

def full_adder(a: bool, b: bool, cin: bool) -> tuple[bool, bool]:
    s = addr3(a, b, cin)                # одна адреса на обидві таблиці
    sum_  = mux_eval(LUT_SUM,  s)
    cout = mux_eval(LUT_COUT, s)
    return sum_, cout
