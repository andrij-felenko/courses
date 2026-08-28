enum LinkState { IDLE, WAIT_ACK };
LinkState st = IDLE;
uint8_t   curSeq;
Cmd       curCmd;
uint32_t  sentAt;
int       tries;

void startSend(uint8_t seq, const Cmd& cmd) {  // поставити команду в чергу
    curSeq = seq; curCmd = cmd; tries = 0;
    sendPacket(curSeq, curCmd); sentAt = millis(); tries = 1;
    st = WAIT_ACK;
}

void linkTick() {                              // викликати щотакту з головного циклу
    if (st != WAIT_ACK) return;
    if (gotAckFor(curSeq)) { st = IDLE; return; }          // підтверджено
    if (millis() - sentAt >= ACK_TIMEOUT) {
        if (tries >= MAX_TRIES) { st = IDLE; failsafe(); return; }  // здаюся
        sendPacket(curSeq, curCmd); sentAt = millis(); tries++;     // повтор
    }
}
