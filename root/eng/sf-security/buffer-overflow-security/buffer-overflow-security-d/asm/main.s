process_user_input:
    pushq   %rbp                ; Збереження базового покажчика кадру caller (8 байтів)
    movq    %rsp, %rbp          ; Встановлення нового базового покажчика кадру
    subq    $80, %rsp           ; Виділення 80 байтів на стеку (64 буфер + 16 вирівнювання)
    movl    %edi, -68(%rbp)     ; Збереження аргументу connection_fd
    leaq    -64(%rbp), %rax     ; Обчислення адреси username_buffer
    movq    %rax, %rsi          ; Передача другого аргументу у read_socket_data
    movl    -68(%rbp), %edi     ; Передача першого аргументу у read_socket_data
    call    read_socket_data    ; Виклик підпрограми зчитування
    leave                       ; Еквівалент: movq %rbp, %rsp; popq %rbp
    ret                         ; Вилучення Saved RIP зі стека у регістр %rip
