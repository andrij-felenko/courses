#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <sstream>
#include <iomanip>

#if defined(_WIN32)
#include <windows.h>
#include <dbghelp.h>
#else
#include <execinfo.h>
#include <dlfcn.h>
#include <cxxabi.h>
#endif

namespace diagnostics {

struct StackFrame {
    size_t index = 0;
    void* address = nullptr;
    std::string symbol_name;
    std::string module_name;
    uintptr_t offset = 0;

    std::string to_string() const {
        std::ostringstream ss;
        ss << "#" << std::setw(2) << std::left << index << " ["
           << address << "] " << symbol_name;
        if (!module_name.empty()) {
            ss << " (файл: " << module_name;
            if (offset > 0) {
                ss << " + 0x" << std::hex << offset;
            }
            ss << ")";
        }
        return ss.str();
    }
};

class StackTracer {
public:
    static std::vector<StackFrame> capture(size_t max_frames = 64) {
        std::vector<StackFrame> frames;
        std::vector<void*> raw_addresses(max_frames);
        SymbolDemangler demangler(1024);

#if defined(_WIN32)
        HANDLE process = GetCurrentProcess();
        SymInitialize(process, NULL, TRUE);

        USHORT captured = RtlCaptureStackBackTrace(
            0,
            static_cast<DWORD>(max_frames),
            raw_addresses.data(),
            NULL
        );

        SYMBOL_INFO_PACKAGE sip;
        sip.si.SizeOfStruct = sizeof(SYMBOL_INFO);
        sip.si.MaxNameLen = sizeof(sip.name);

        for (USHORT i = 0; i < captured; ++i) {
            DWORD64 addr = reinterpret_cast<DWORD64>(raw_addresses[i]);
            DWORD64 displacement = 0;
            std::string sym = "<невідомий символ>";
            std::string mod = "<головний модуль>";

            if (SymFromAddr(process, addr, &displacement, &sip.si)) {
                sym = demangler.demangle(sip.si.Name);
            }

            IMAGEHLP_MODULE64 mod_info;
            mod_info.SizeOfStruct = sizeof(IMAGEHLP_MODULE64);
            if (SymGetModuleInfo64(process, addr, &mod_info)) {
                mod = mod_info.ModuleName;
            }

            frames.push_back(StackFrame{
                .index = i,
                .address = raw_addresses[i],
                .symbol_name = std::move(sym),
                .module_name = std::move(mod),
                .offset = static_cast<uintptr_t>(displacement)
            });
        }
#else
        int captured = backtrace(raw_addresses.data(), static_cast<int>(max_frames));

        for (int i = 0; i < captured; ++i) {
            Dl_info info;
            std::string sym = "<невідомий символ>";
            std::string mod = "<динамічний об'єкт>";
            uintptr_t offset = 0;

            if (dladdr(raw_addresses[i], &info)) {
                if (info.dli_sname) {
                    sym = demangler.demangle(info.dli_sname);
                    offset = reinterpret_cast<uintptr_t>(raw_addresses[i]) -
                             reinterpret_cast<uintptr_t>(info.dli_saddr);
                }
                if (info.dli_fname) {
                    mod = info.dli_fname;
                }
            }

            frames.push_back(StackFrame{
                .index = static_cast<size_t>(i),
                .address = raw_addresses[i],
                .symbol_name = std::move(sym),
                .module_name = std::move(mod),
                .offset = offset
            });
        }
#endif
        return frames;
    }
};

} // namespace diagnostics

// Ієрархія бізнес-логіки для демонстрації стек-трейсу
namespace core::engine {

template <typename PhysicsModel>
class SimulationPipeline {
public:
    void execute_step(double delta_time) {
        process_collisions(delta_time);
    }

private:
    void process_collisions(double dt) {
        PhysicsModel model;
        model.calculate_forces(dt);
    }
};

class RigidBodySolver {
public:
    void calculate_forces(double dt) {
        solve_constraints(dt);
    }

private:
    void solve_constraints([[maybe_unused]] double dt) {
        auto trace = diagnostics::StackTracer::capture();
        std::cout << "\n=== ЗАХОПЛЕНИЙ СТЕК-ТРЕЙС ВИКЛИКІВ ===\n";
        for (const auto& frame : trace) {
            std::cout << frame.to_string() << '\n';
        }
        std::cout << "======================================\n\n";
    }
};

} // namespace core::engine

int main() {
    core::engine::SimulationPipeline<core::engine::RigidBodySolver> pipeline;
    pipeline.execute_step(0.0166);
    return 0;
}
