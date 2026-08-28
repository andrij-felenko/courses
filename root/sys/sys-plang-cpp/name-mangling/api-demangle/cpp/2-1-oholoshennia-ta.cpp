#include <windows.h>
#include <dbghelp.h>

#pragma comment(lib, "dbghelp.lib")

DWORD WINAPI UnDecorateSymbolName(
    PCSTR DecoratedName,
    PSTR  UnDecoratedName,
    DWORD UndecoratedLength,
    DWORD Flags
);
