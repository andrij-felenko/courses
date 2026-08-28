/* Керування послідовним портом через Win32 API на мові C */
#include <windows.h>

BOOL win32_send_break(HANDLE hSerial, DWORD duration_ms) {
    /* Перемикання лінії TX у стан Space (логічний нуль) */
    if (!SetCommBreak(hSerial)) return FALSE;
    Sleep(duration_ms);
    /* Повернення лінії TX у стан Mark (логічна одиниця) */
    return ClearCommBreak(hSerial);
}
