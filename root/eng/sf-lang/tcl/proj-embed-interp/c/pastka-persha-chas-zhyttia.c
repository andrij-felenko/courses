static int RunTwiceCmd(void *cd, Tcl_Interp *interp,
                       int objc, Tcl_Obj *const objv[]) {
    if (objc != 2) {
        Tcl_WrongNumArgs(interp, 1, objv, "body");
        return TCL_ERROR;
    }

    Tcl_Obj *body = objv[1];
    Tcl_IncrRefCount(body);        // ← «це моє»: підняли лічильник, тепер eval його не звільнить

    int rc = Tcl_EvalObjEx(interp, body, 0);      // виконали тіло раз
    if (rc == TCL_OK) {
        rc = Tcl_EvalObjEx(interp, body, 0);      // і вдруге — body ГАРАНТОВАНО ще живий
    }

    Tcl_DecrRefCount(body);        // ← відпустили; якщо ми були останні — звільниться тут
    return rc;
}
