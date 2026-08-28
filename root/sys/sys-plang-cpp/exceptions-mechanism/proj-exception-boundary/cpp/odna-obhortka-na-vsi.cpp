#define PARSER_BUILDING
#include "parser.h"

#include <cstdio>
#include <exception>
#include <new>
#include <stdexcept>
#include <system_error>
#include <utility>

#include "cfg/parser.hpp"   // справжня реалізація: кидає так, як їй зручно

// Неповний тип із заголовка стає повним рівно тут — і далі нікуди не витікає.
struct parser_ctx {
    cfg::Parser        impl;
    std::exception_ptr failure;              // сам об'єкт відмови, а не переказ
    char               message[256] = "ok";  // масив, а не std::string: повідомити
};                                           // про вичерпану пам'ять теж треба

namespace {

// snprintf нічого не виділяє й нічого не кидає — саме тому не рядок.
void set_message(parser_ctx* ctx, const char* text) noexcept {
    std::snprintf(ctx->message, sizeof ctx->message, "%s", text ? text : "");
}

// НЕ шаблон: ланцюг catch потрапляє в бінарник рівно один раз.
// Порядок гілок — від похідних до базових: перемагає перша підхожа.
parser_status record(parser_ctx* ctx, std::exception_ptr e) noexcept {
    ctx->failure = e;                       // присвоєння exception_ptr — noexcept
    try {
        std::rethrow_exception(e);
    }
    catch (const cfg::SyntaxError& ex)      { set_message(ctx, ex.what());
                                              return PARSER_E_SYNTAX; }
    catch (const std::bad_alloc&)           { set_message(ctx, "out of memory");
                                              return PARSER_E_NO_MEMORY; }
    catch (const std::system_error& ex)     { set_message(ctx, ex.what());
                                              return PARSER_E_IO; }
    catch (const std::invalid_argument& ex) { set_message(ctx, ex.what());
                                              return PARSER_E_ARG; }
    catch (const std::exception& ex)        { set_message(ctx, ex.what());
                                              return PARSER_E_INTERNAL; }
    catch (...)                             { set_message(ctx, "unknown exception");
                                              return PARSER_E_INTERNAL; }
}

// Обгортка межі. Тіло навмисно крихітне — усе, що можна винести з шаблона,
// винесено в record().
template <class Fn>
parser_status boundary(parser_ctx* ctx, Fn&& fn) noexcept {
    if (!ctx) return PARSER_E_ARG;
    try {
        set_message(ctx, "ok");
        ctx->failure = nullptr;
        std::forward<Fn>(fn)();
        return PARSER_OK;
    } catch (...) {
        return record(ctx, std::current_exception());
    }
}

} // namespace
