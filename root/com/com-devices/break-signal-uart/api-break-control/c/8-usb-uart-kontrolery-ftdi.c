/* Керування Break через бібліотеки FTDI D2XX та Silicon Labs VCP на мові C */
#include <ftd2xx.h>

/* FTDI D2XX API */
FT_STATUS ftdi_set_break_on(FT_HANDLE ftHandle) {
    return FT_SetBreakOn(ftHandle);
}

FT_STATUS ftdi_set_break_off(FT_HANDLE ftHandle) {
    return FT_SetBreakOff(ftHandle);
}
