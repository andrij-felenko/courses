// Залити три задачні області з TCB прямо в регістри MPU.
// Викликається на кожному перемиканні контексту → мусить бути швидкою.
static void mpu_load_task(const TCB *t)
{
    // Записуємо RBAR/RASR парами. Номер області (REGION) уже зашитий
    // у полі RBAR кожного запису, тож RNR чіпати не треба:
    // біт VALID у RBAR каже залізу «номер бери з поля REGION».
    for (int i = 0; i < TASK_REGIONS; i++) {
        MPU->RBAR = t->regions[i].rbar;   // база + VALID + REGION
        MPU->RASR = t->regions[i].rasr;   // права/розмір/дозвіл
    }
}
