#include <Arduino.h>
#include <array>

enum class VmError : uint8_t {
    None            = 0x00,
    StackOverflow   = 0x01,
    StackUnderflow  = 0x02,
    InvalidOpcode   = 0x03,
    OutOfBounds     = 0x04
};

struct CrashDump {
    VmError error{VmError::None};
    uint16_t fault_ip{0};
    uint8_t fault_sp{0};
    std::array<uint16_t, 8> stack_snapshot{};
    std::array<uint16_t, 4> regs_snapshot{};

    void printToSerial() const {
        Serial.print(F("[VM CRASH DUMP] Error Code: 0x"));
        Serial.print(static_cast<uint8_t>(error), HEX);
        Serial.print(F(" at IP: 0x"));
        Serial.println(fault_ip, HEX);
        for (uint8_t i = 0; i < fault_sp && i < 8; ++i) {
            Serial.print(F("  Stack["));
            Serial.print(i);
            Serial.print(F("] = 0x"));
            Serial.println(stack_snapshot[i], HEX);
        }
    }
};

class VmDiagnostics {
public:
    static void logTrace(uint16_t ip, uint8_t opcode) {
        Serial.print(F("TRACE IP: 0x"));
        Serial.print(ip, HEX);
        Serial.print(F(" | OP: 0x"));
        Serial.println(opcode, HEX);
    }

    static void handleCrash(VmError err, uint16_t ip, uint8_t sp, 
                            const uint16_t* stack, const uint16_t* regs) {
        CrashDump dump;
        dump.error = err;
        dump.fault_ip = ip;
        dump.fault_sp = sp;
        for (size_t i = 0; i < sp && i < 8; ++i) dump.stack_snapshot[i] = stack[i];
        for (size_t i = 0; i < 4; ++i) dump.regs_snapshot[i] = regs[i];
        
        dump.printToSerial();
    }
};
