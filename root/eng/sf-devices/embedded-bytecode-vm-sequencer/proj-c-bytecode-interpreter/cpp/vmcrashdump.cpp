struct VmCrashDump {
	uint32_t timestamp_ms;
	uint16_t ip;
	uint8_t opcode;
	uint8_t errorCode;
	uint8_t sp;
	uint16_t stack[8];
	int16_t regs[4];
};

VmCrashDump BytecodeVM::createCrashDump(uint8_t errCode, uint8_t faultOpcode) const noexcept {
	VmCrashDump dump{};
	dump.timestamp_ms = state_.waitUntilMs;
	dump.ip = state_.ip;
	dump.opcode = faultOpcode;
	dump.errorCode = errCode;
	dump.sp = state_.sp;
	for (std::size_t i = 0; i < 8; ++i) {
		dump.stack[i] = state_.stack[i];
	}
	for (std::size_t i = 0; i < 4; ++i) {
		dump.regs[i] = state_.regs[i];
	}
	return dump;
}
