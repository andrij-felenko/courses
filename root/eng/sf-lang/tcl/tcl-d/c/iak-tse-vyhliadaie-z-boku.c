#include <tcl.h>

int main(void) {
    Tcl_Interp *interp = Tcl_CreateInterp();     // створити тлумач Tcl

    // виконати рядок Tcl як код і забрати результат
    if (Tcl_Eval(interp, "expr {40 + 2}") == TCL_OK) {
        const char *res = Tcl_GetStringResult(interp);   // результат — завжди рядок
        printf("Tcl порахував: %s\n", res);              // друкує: Tcl порахував: 42
    }

    Tcl_DeleteInterp(interp);
    return 0;
}
