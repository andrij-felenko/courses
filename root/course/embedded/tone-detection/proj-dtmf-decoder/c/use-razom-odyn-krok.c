dtmf_fsm_t fsm;

void dtmf_decoder_init(void)
{
    dtmf_init((dtmf_bank_t *)&bank);
    dtmf_fsm_init(&fsm);
    block_ready = 0;
}

// кликати в головному циклі; повертає підтверджену цифру або 0
char dtmf_decoder_poll(void)
{
    if (!block_ready)
        return 0;

    // забрати готовий блок, не наражаючись на гонитву з ISR
    dtmf_bank_t snapshot;
    __disable_irq();
    snapshot    = *(dtmf_bank_t *)&bank;   // копія станів і енергії
    dtmf_init((dtmf_bank_t *)&bank);       // СКИДАННЯ під наступний блок!
    block_ready = 0;
    __enable_irq();

    char sym = dtmf_classify(&snapshot);   // сирий вердикт блоку
    return dtmf_fsm_step(&fsm, sym);       // підтверджена подія або 0
}
