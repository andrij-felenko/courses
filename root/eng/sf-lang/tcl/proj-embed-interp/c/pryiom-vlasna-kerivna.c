static int RepeatCmd(void *cd, Tcl_Interp *interp,
                     int objc, Tcl_Obj *const objv[]) {
    if (objc != 3) {                                  // repeat + число + тіло
        Tcl_WrongNumArgs(interp, 1, objv, "count body");
        return TCL_ERROR;
    }

    int count;
    if (Tcl_GetIntFromObj(interp, objv[1], &count) != TCL_OK) {
        return TCL_ERROR;                             // перший аргумент не число
    }

    Tcl_Obj *body = objv[2];
    Tcl_IncrRefCount(body);                           // утримуємо тіло на весь цикл

    int rc = TCL_OK;
    for (int i = 0; i < count; i++) {
        rc = Tcl_EvalObjEx(interp, body, 0);          // виконати тіло в кадрі викликача
        if (rc == TCL_BREAK) { rc = TCL_OK; break; }  // тіло сказало break — чемно вийти
        if (rc == TCL_CONTINUE) { rc = TCL_OK; continue; }
        if (rc != TCL_OK) break;                      // помилка чи return — припинити цикл
    }

    Tcl_DecrRefCount(body);
    return rc;
}
