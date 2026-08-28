#include <tcl.h>
#include <stdio.h>

int main(void) {
    Tcl_Interp *interp = Tcl_CreateInterp();   // 1. народити тлумач зі словником вбудованих команд

    // 2. згодувати рядок Tcl як код; повертає TCL_OK або TCL_ERROR
    int rc = Tcl_Eval(interp, "expr {40 + 2}");

    if (rc == TCL_OK) {
        const char *res = Tcl_GetStringResult(interp);   // 3. результат — завжди рядок
        printf("порахувало: %s\n", res);                 // друкує: порахувало: 42
    } else {
        // на помилці в результаті лежить текст помилки — теж читаємо як рядок
        printf("помилка: %s\n", Tcl_GetStringResult(interp));
    }

    Tcl_DeleteInterp(interp);   // 4. знищити тлумач, звільнити всю його пам'ять
    return 0;
}
