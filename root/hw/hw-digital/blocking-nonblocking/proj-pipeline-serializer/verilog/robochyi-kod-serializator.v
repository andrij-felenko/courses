module uart_tx #(
    parameter DBITS = 8
)(
    input            clk,
    input            start,        // імпульс "почати передачу"
    input      [DBITS-1:0] data,   // байт для відправлення
    output reg       tx,           // послідовний вихід
    output reg       busy          // 1, доки триває передача
);
    reg [DBITS+1:0] shreg;         // 10 біт: {стоп, дані[7:0], старт}
    reg [3:0]       bitcnt;        // скільки біт лишилося вислати

    initial begin
        tx   = 1'b1;               // лінія в спокої = 1
        busy = 1'b0;
    end

    always @(posedge clk) begin
        if (start && !busy) begin
            // ЗАВАНТАЖЕННЯ кадру: старт=0 знизу, дані, стоп=1 зверху
            shreg  <= {1'b1, data, 1'b0};
            bitcnt <= DBITS + 2;   // 10 біт до відправлення
            busy   <= 1'b1;
        end else if (busy) begin
            // ЗСУВ: молодший біт — у лінію, решта зсувається вниз
            tx     <= shreg[0];
            shreg  <= {1'b1, shreg[DBITS+1:1]};  // згори вдвигаємо 1 (спокій)
            bitcnt <= bitcnt - 1'b1;
            if (bitcnt == 1)
                busy <= 1'b0;      // останній біт пішов — вільні
        end
    end
endmodule
