#include <cstdio>
#include <string>
#include <vector>
#include <map>

// Чотири вентилі — кожен це елементарна дія над бітами
enum class Op { And, Or, Xor, Not };

int gate(Op op, int a, int b) {
    switch (op) {
        case Op::And: return a & b;   // 1 лише коли обидва 1
        case Op::Or:  return a | b;   // 1 коли хоч один 1
        case Op::Xor: return a ^ b;   // 1 коли біти різні
        case Op::Not: return 1 - a;   // перевертає 0↔1 (b не потрібен)
    }
    return 0;
}
