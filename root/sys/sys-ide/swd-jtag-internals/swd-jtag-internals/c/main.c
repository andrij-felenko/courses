// Поля 8-бітного запиту SWD (молодший біт першим: start..park)
#define SWD_READ_DP_IDCODE  0xA5   // start=1 APnDP=0 RnW=1 A2=0 A3=0 par=1 stop=0 park=1

uint8_t  ack;            // 3 біти: 001=OK, 010=WAIT, 100=FAULT
uint32_t idcode;
swd_send_request(SWD_READ_DP_IDCODE);   // 8 біт запиту
ack = swd_read_ack();                    // turnaround + 3 біти
if (ack == 0b001) {                      // OK
    idcode = swd_read_data();            // 32 біти + парність + turnaround
}
