#include <visa.h>
#include <stdio.h>
#include <string.h>

int main() {
    ViSession defaultRM, stageSession;
    char buffer[256];

    viOpenDefaultRM(&defaultRM);
    viOpen(defaultRM, "USB0::0x1AB1::0x0111::STAGE12345::INSTR", VI_NULL, VI_NULL, &stageSession);

    // Надсилання запиту *IDN?
    viPrintf(stageSession, "*IDN?\n");
    viScanf(stageSession, "%255s", buffer);
    printf("Запущено контролер: %s\n", buffer);

    // Команда на переміщення в позицію Z = 25.0 мм
    viPrintf(stageSession, "POSITION:MOVE:ABSOLUTE 25.0\n");

    viClose(stageSession);
    viClose(defaultRM);
    return 0;
}
