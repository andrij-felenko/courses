typedef struct { uint8_t op, rd, rs1, rs2; uint16_t addr; } Instr;

// Проста програма: п'ять справжніх команд, тоді HALT.
//   0: LOAD  r1,[0x20]      r1 <- пам'ять[0x20]
//   1: LOAD  r2,[0x21]      r2 <- пам'ять[0x21]
//   2: ADD   r3,r5,r6       r3 <- r5 + r6
//   3: STORE [0x22],r7      пам'ять[0x22] <- r7
//   4: ADD   r4,r5,r5       r4 <- r5 + r5
//   5: HALT
static const Instr PROG[] = {
    { OP_LOAD,  1, 0, 0, 0x20 },
    { OP_LOAD,  2, 0, 0, 0x21 },
    { OP_ADD,   3, 5, 6, 0    },
    { OP_STORE, 0, 7, 0, 0x22 },
    { OP_ADD,   4, 5, 5, 0    },
    { OP_HALT,  0, 0, 0, 0    },
};
#define PROG_LEN ((uint16_t)(sizeof(PROG)/sizeof(PROG[0])))
