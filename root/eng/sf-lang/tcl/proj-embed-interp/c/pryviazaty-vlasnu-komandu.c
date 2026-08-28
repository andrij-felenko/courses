#include <tcl.h>
#include <string.h>

// уявна апаратна функція прошивки
extern void hw_set_led(int on);

// C-функція, що стане Tcl-командою "led".
// Сигнатура задана бібліотекою — міняти її не можна:
//   clientData — довільний вказівник, який ми передали при реєстрації (тут не треба);
//   interp     — тлумач, у чий результат ми кладемо відповідь чи помилку;
//   objc       — скільки слів у команді, ВКЛЮЧНО з іменем "led";
//   objv       — масив слів-значень; objv[0] — саме ім'я "led", objv[1] — перший аргумент.
static int LedCmd(void *clientData, Tcl_Interp *interp,
                  int objc, Tcl_Obj *const objv[]) {
    if (objc != 2) {                                  // чекаємо рівно 1 аргумент після імені
        // стандартний спосіб поскаржитися на кількість: сам складе гарне повідомлення
        Tcl_WrongNumArgs(interp, 1, objv, "on|off");
        return TCL_ERROR;
    }

    const char *arg = Tcl_GetString(objv[1]);         // беремо аргумент як рядок
    if (strcmp(arg, "on") == 0) {
        hw_set_led(1);
    } else if (strcmp(arg, "off") == 0) {
        hw_set_led(0);
    } else {
        // кладемо СВІЙ текст помилки в результат тлумача й сигналимо біду
        Tcl_SetObjResult(interp, Tcl_NewStringObj("led: чекав on або off", -1));
        return TCL_ERROR;
    }
    return TCL_OK;      // успіх; результат лишаємо порожнім
}

int main(void) {
    Tcl_Interp *interp = Tcl_CreateInterp();

    // прив'язати ім'я "led" до нашої C-функції; NULL — це clientData й deleteProc
    Tcl_CreateObjCommand(interp, "led", LedCmd, NULL, NULL);

    // тепер у будь-якому скрипті слово "led" кличе наш C-код:
    Tcl_Eval(interp, "led on");
    Tcl_Eval(interp, "for {set i 0} {$i < 3} {incr i} { led on; led off }");

    Tcl_DeleteInterp(interp);
    return 0;
}
