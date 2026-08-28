// Однорозрядний повний суматор двома мультиплексорами 8→1,
// що адресуються тими самими трьома бітами (a — старший, cin — молодший).
//                  abc: 000 001 010 011 100 101 110 111
static const uint8_t LUT_SUM [8] = { 0,  1,  1,  0,  1,  0,  0,  1 };   // = XOR3
static const uint8_t LUT_COUT[8] = { 0,  0,  0,  1,  0,  1,  1,  1 };   // = MAJ3

void full_adder(bool a, bool b, bool cin, bool *sum, bool *cout) {
    uint32_t s = addr3(a, b, cin);      // одна адреса на обидві таблиці
    *sum  = mux_eval(LUT_SUM,  s);
    *cout = mux_eval(LUT_COUT, s);
}
