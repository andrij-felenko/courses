/* Кодування 3VL:
   TRI_FALSE:   val=0, is_known=1
   TRI_TRUE:    val=1, is_known=1
   TRI_UNKNOWN: val=0, is_known=0
*/
typedef struct {
    uint8_t val;      /* 0 або 1 */
    uint8_t is_known; /* 1 - визначено, 0 - UNKNOWN */
} TriBool;

TriBool tri_make_bool(bool b) {
    TriBool res = { (uint8_t)(b ? 1 : 0), 1 };
    return res;
}

TriBool tri_make_unknown(void) {
    TriBool res = { 0, 0 };
    return res;
}

TriBool tri_and(TriBool a, TriBool b) {
    TriBool res;
    /* Якщо хоча б один FALSE (val=0, is_known=1) -> результат FALSE */
    if ((a.is_known && a.val == 0) || (b.is_known && b.val == 0)) {
        res.val = 0;
        res.is_known = 1;
    } else if (a.is_known && b.is_known) {
        res.val = a.val & b.val;
        res.is_known = 1;
    } else {
        res.val = 0;
        res.is_known = 0; /* UNKNOWN */
    }
    return res;
}

TriBool tri_or(TriBool a, TriBool b) {
    TriBool res;
    /* Якщо хоча б один TRUE (val=1, is_known=1) -> результат TRUE */
    if ((a.is_known && a.val == 1) || (b.is_known && b.val == 1)) {
        res.val = 1;
        res.is_known = 1;
    } else if (a.is_known && b.is_known) {
        res.val = a.val | b.val;
        res.is_known = 1;
    } else {
        res.val = 0;
        res.is_known = 0; /* UNKNOWN */
    }
    return res;
}

TriBool tri_not(TriBool a) {
    TriBool res;
    if (!a.is_known) {
        res.val = 0;
        res.is_known = 0;
    } else {
        res.val = (uint8_t)(1 - a.val);
        res.is_known = 1;
    }
    return res;
}
