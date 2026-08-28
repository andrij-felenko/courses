extern void hw_set_pwm(int duty);

static int PwmCmd(void *cd, Tcl_Interp *interp,
                  int objc, Tcl_Obj *const objv[]) {
    if (objc != 2) {
        Tcl_WrongNumArgs(interp, 1, objv, "duty");
        return TCL_ERROR;
    }

    int duty;
    // розібрати аргумент як ціле; якщо це не число — САМА покладе помилку в результат
    if (Tcl_GetIntFromObj(interp, objv[1], &duty) != TCL_OK) {
        return TCL_ERROR;        // текст «expected integer but got …» уже в результаті
    }
    if (duty < 0 || duty > 255) {
        Tcl_SetObjResult(interp, Tcl_NewStringObj("pwm: шпаруватість поза 0..255", -1));
        return TCL_ERROR;
    }

    hw_set_pwm(duty);

    // повернути в скрипт фактично встановлене значення — теж через Tcl_Obj
    Tcl_SetObjResult(interp, Tcl_NewIntObj(duty));
    return TCL_OK;
}
