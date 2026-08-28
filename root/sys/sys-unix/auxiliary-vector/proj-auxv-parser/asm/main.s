.global _start
.type _start, @function
_start:
    xor %rbp, %rbp          /* Обнуляємо rbp для коректного unwinding відлагоджувача */
    mov (%rsp), %rdi        /* Перший аргумент C: argc (або сам %rsp) */
    mov %rsp, %rdi          /* Передаємо початковий вказівник %rsp у C-функцію */
    call parse_raw_stack_frame
    
    mov $60, %rax           /* Системний виклик exit (sys_exit) */
    xor %rdi, %rdi          /* Код повернення 0 */
    syscall
