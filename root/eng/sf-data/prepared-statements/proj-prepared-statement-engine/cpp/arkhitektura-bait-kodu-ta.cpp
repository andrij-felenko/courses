#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <variant>
#include <optional>
#include <span>
#include <unordered_map>
#include <cstring>
#include <cstdint>

struct UserRecord {
    int64_t id;
    std::string name;
};

using Value = std::variant<int64_t, std::string>;

enum class Opcode {
    ScanBegin,
    CheckIdEqParam,
    CheckNameEqParam,
    EmitRow,
    ScanNext,
    Halt
};

struct Instruction {
    Opcode op;
    size_t param_idx{0};
};

class PreparedPlan {
public:
    std::vector<Instruction> instructions;
    size_t param_count{0};
    std::string template_sql;

    static std::optional<PreparedPlan> compile(std::string_view sql) {
        PreparedPlan plan;
        plan.template_sql = std::string(sql);

        if (sql.find("WHERE id = ?") != std::string_view::npos) {
            plan.instructions = {
                {Opcode::ScanBegin, 0},
                {Opcode::CheckIdEqParam, 0},
                {Opcode::EmitRow, 0},
                {Opcode::ScanNext, 0},
                {Opcode::Halt, 0}
            };
            plan.param_count = 1;
            return plan;
        } else if (sql.find("WHERE name = ?") != std::string_view::npos) {
            plan.instructions = {
                {Opcode::ScanBegin, 0},
                {Opcode::CheckNameEqParam, 0},
                {Opcode::EmitRow, 0},
                {Opcode::ScanNext, 0},
                {Opcode::Halt, 0}
            };
            plan.param_count = 1;
            return plan;
        }
        return std::nullopt;
    }
};

class VirtualMachine {
public:
    static std::vector<UserRecord> execute(
        const PreparedPlan& plan,
        std::span<const Value> params,
        std::span<const UserRecord> table)
    {
        std::vector<UserRecord> results;
        size_t ip = 0;
        size_t cursor = 0;
        bool match = false;

        while (ip < plan.instructions.size()) {
            const auto& inst = plan.instructions[ip];
            switch (inst.op) {
                case Opcode::ScanBegin:
                    cursor = 0;
                    match = false;
                    ++ip;
                    break;

                case Opcode::CheckIdEqParam:
                    if (cursor < table.size() && inst.param_idx < params.size()) {
                        if (std::holds_alternative<int64_t>(params[inst.param_idx])) {
                            match = (table[cursor].id == std::get<int64_t>(params[inst.param_idx]));
                        }
                    }
                    ++ip;
                    break;

                case Opcode::CheckNameEqParam:
                    if (cursor < table.size() && inst.param_idx < params.size()) {
                        if (std::holds_alternative<std::string>(params[inst.param_idx])) {
                            match = (table[cursor].name == std::get<std::string>(params[inst.param_idx]));
                        }
                    }
                    ++ip;
                    break;

                case Opcode::EmitRow:
                    if (match && cursor < table.size()) {
                        results.push_back(table[cursor]);
                    }
                    ++ip;
                    break;

                case Opcode::ScanNext:
                    ++cursor;
                    if (cursor < table.size()) {
                        ip = 1; // перехід до початку перевірок для нового рядка
                    } else {
                        ++ip;
                    }
                    break;

                case Opcode::Halt:
                    return results;
            }
        }
        return results;
    }
};
