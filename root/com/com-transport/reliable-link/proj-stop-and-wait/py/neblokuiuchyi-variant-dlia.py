IDLE, WAIT_ACK = 0, 1

st = IDLE
cur_seq = 0
cur_cmd = None
sent_at = 0
tries = 0

def start_send(seq, cmd):                      # поставити команду в чергу
    global st, cur_seq, cur_cmd, sent_at, tries
    cur_seq, cur_cmd = seq, cmd
    send_packet(cur_seq, cur_cmd); sent_at = millis(); tries = 1
    st = WAIT_ACK

def link_tick():                               # викликати щотакту з головного циклу
    global st, sent_at, tries
    if st != WAIT_ACK:
        return
    if got_ack_for(cur_seq):                   # підтверджено
        st = IDLE; return
    if millis() - sent_at >= ACK_TIMEOUT:
        if tries >= MAX_TRIES:                 # здаюся
            st = IDLE; failsafe(); return
        send_packet(cur_seq, cur_cmd); sent_at = millis(); tries += 1  # повтор
