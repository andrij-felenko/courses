module uart_tx #(
    parameter integer DIV = 1250   // тактів на біт: 12 МГц / 9600 бод = 1250
)(
    input        clk,      // тактовий генератор плати
    input        start,    // імпульс "відправ байт" (на один такт)
    input  [7:0] data,     // байт, який передаємо
    output       tx,       // лінія передачі, у спокої = 1
    output       busy      // 1, поки кадр іще йде
);
    reg [12:0] div     = 0;        // дільник бода: рахує такти в межах одного біта
    reg [9:0]  shreg   = 10'h3FF;  // зсувний реєстр кадру (у спокої — усі одиниці)
    reg [3:0]  bitcnt  = 0;        // скільки бітів кадру ще лишилось виштовхнути
    reg        sending = 0;        // 1 = передаємо, 0 = спокій

    wire tick = (div == DIV-1);    // рівно один імпульс на бітовий інтервал

    always @(posedge clk) begin
        if (!sending) begin                    // спокій: чекаємо на start
            div <= 0;
            if (start) begin
                shreg   <= {1'b1, data, 1'b0}; // стоп(1) + 8 даних + старт(0)
                bitcnt  <= 10;                 // усього 10 бітів у кадрі
                sending <= 1;
            end
        end else begin                         // передача кадру
            div <= tick ? 0 : div + 1;
            if (tick) begin                    // лише на межі біта!
                shreg  <= {1'b1, shreg[9:1]};  // зсув праворуч, зверху вливаємо 1
                bitcnt <= bitcnt - 1;
                if (bitcnt == 1)               // останній біт щойно виданий —
                    sending <= 0;              // ...повертаємось у спокій
            end
        end
    end

    assign tx   = shreg[0];   // молодший біт кадру — постійно в лінії
    assign busy = sending;
endmodule
