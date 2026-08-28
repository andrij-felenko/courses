# ====================================================================
# ЗГЕНЕРОВАНИЙ JIT-КОД BPF TRAMPOLINE ДЛЯ X86_64
# ====================================================================

# 1. Пролог: створення кадру стеку
push   rbp
mov    rbp, rsp
sub    rsp, 0x30                  # Виділення 48 байтів на стеку

# 2. Збереження вхідних аргументів у масив args[] на стеку
mov    QWORD PTR [rbp-0x18], rdi  # args[0] = перший аргумент (RDI)
mov    QWORD PTR [rbp-0x10], rsi  # args[1] = другий аргумент (RSI)

# 3. Виклик BPF-програми fentry
lea    rdi, [rbp-0x18]            # RDI = адреса масиву args[] (контекст ctx)
mov    rax, 0xffffffffc03a1050    # RAX = адреса JIT-коду BPF fentry програми
call   rax                        # Прямий виклик BPF-програми

# 4. Виклик оригінальної функції ядра
mov    rdi, QWORD PTR [rbp-0x18]  # Відновлення RDI з args[0]
mov    rsi, QWORD PTR [rbp-0x10]  # Відновлення RSI з args[1]
mov    rax, 0xffffffff81234567    # RAX = адреса оригінальної функції ядра
call   rax                        # Виконання оригінальної функції

# 5. Збереження значення повернення
mov    QWORD PTR [rbp-0x8], rax   # args[2] = retval (результат з RAX)

# 6. Виклик BPF-програми fexit
lea    rdi, [rbp-0x18]            # RDI = адреса args[] (включаючи retval)
mov    rax, 0xffffffffc03a1100    # RAX = адреса JIT-коду BPF fexit програми
call   rax                        # Прямий виклик BPF fexit програми

# 7. Епілог: відновлення стану та повернення
mov    rax, QWORD PTR [rbp-0x8]   # RAX = оригінальний retval
leave                             # mov rsp, rbp; pop rbp
ret                               # Повернення викликаючому коду
