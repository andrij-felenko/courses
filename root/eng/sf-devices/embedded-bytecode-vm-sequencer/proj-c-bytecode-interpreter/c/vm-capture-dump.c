typedef struct {
	uint32_t timestamp_ms;
	uint16_t ip;
	uint8_t opcode;
	uint8_t error_code;
	uint8_t sp;
	uint16_t stack[8];
	int16_t regs[4];
} vm_crash_dump_t;

void vm_capture_dump(const vm_state_t *vm, uint8_t err, uint8_t op, vm_crash_dump_t *dump) {
	dump->timestamp_ms = vm->wait_until_ms;
	dump->ip = vm->ip;
	dump->opcode = op;
	dump->error_code = err;
	dump->sp = vm->sp;
	for (uint8_t i = 0; i < 8; ++i) {
		dump->stack[i] = vm->stack[i];
	}
	for (uint8_t i = 0; i < 4; ++i) {
		dump->regs[i] = vm->regs[i];
	}
}
