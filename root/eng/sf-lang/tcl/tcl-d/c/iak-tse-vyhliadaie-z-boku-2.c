// C-функція, що стане командою Tcl на ім'я "led"
static int LedCmd(void *data, Tcl_Interp *interp, int objc, Tcl_Obj *const objv[]) {
    if (objc != 2) {                                     // очікуємо рівно 1 аргумент
        Tcl_WrongNumArgs(interp, 1, objv, "on|off");
        return TCL_ERROR;
    }
    const char *arg = Tcl_GetString(objv[1]);            // аргумент як рядок
    set_led(strcmp(arg, "on") == 0);                     // наша апаратна дія
    return TCL_OK;
}

int main(void) {
    Tcl_Interp *interp = Tcl_CreateInterp();
    // прив'язати ім'я "led" до нашої C-функції
    Tcl_CreateObjCommand(interp, "led", LedCmd, NULL, NULL);

    Tcl_Eval(interp, "led on");    // Tcl-скрипт кличе наш C-код → світлодіод засвітився
    Tcl_DeleteInterp(interp);
    return 0;
}
