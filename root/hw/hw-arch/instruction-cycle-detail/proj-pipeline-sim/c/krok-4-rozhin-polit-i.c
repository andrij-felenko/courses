static bool pipeline_busy(const CPU *c)
{
    for (int i = 0; i < NLATCH; i++) if (c->L[i].valid) return true;
    return !c->fetch_halted && c->pc < PROG_LEN;   // ще є що вибирати?
}

int main(void)
{
    CPU c = (CPU){0};
    c.dmem[0x20] = 10; c.dmem[0x21] = 32;        // дані для LOAD
    c.reg[5] = 5; c.reg[6] = 6; c.reg[7] = 99;   // операнди для ADD/STORE

    for (int t = 1; pipeline_busy(&c) && t < 100; t++) {
        tick(&c);
        printf("такт %d:  IF/ID valid=%d  ID/EX valid=%d  EX/MEM valid=%d  MEM/WB valid=%d\n",
               t, c.L[IF_ID].valid, c.L[ID_EX].valid, c.L[EX_MEM].valid, c.L[MEM_WB].valid);
    }
    printf("r1=%d r2=%d r3=%d r4=%d  пам'ять[0x22]=%d\n",
           c.reg[1], c.reg[2], c.reg[3], c.reg[4], c.dmem[0x22]);
    return 0;
}
