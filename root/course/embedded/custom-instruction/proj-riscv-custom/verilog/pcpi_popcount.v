// pcpi_popcount.v — обгортка PCPI навколо popcount_unit.
// Підключається до готових сигналів PicoRV32; ядро не змінюємо.
module pcpi_popcount (
    input  wire        clk,
    input  wire        resetn,
    input  wire        pcpi_valid,   // ядро пропонує невпізнану команду
    input  wire [31:0] pcpi_insn,    // повний код команди
    input  wire [31:0] pcpi_rs1,     // значення rs1 (наш вхід)
    input  wire [31:0] pcpi_rs2,     // значення rs2 (не потрібне popcount)
    output reg         pcpi_wr,      // ми хочемо записати rd
    output reg  [31:0] pcpi_rd,      // результат
    output reg         pcpi_wait,    // нам треба ще такти (тут — ні)
    output reg         pcpi_ready    // ми закінчили
);
    // --- Розпізнавання НАШОЇ команди (ті самі біти, що в кодуванні!) ---
    wire is_ours = pcpi_valid
                 && (pcpi_insn[6:0]   == 7'b0001011)   // opcode = custom-0
                 && (pcpi_insn[14:12] == 3'b000)       // funct3 = 0
                 && (pcpi_insn[31:25] == 7'b0000000);  // funct7 = 0

    wire [5:0] cnt;
    popcount_unit u_pc (.a(pcpi_rs1), .count(cnt));    // комбінаційно рахуємо

    always @(posedge clk) begin
        // За замовчуванням мовчимо: це НЕ наша команда -> хай ядро шукає далі
        pcpi_wr    <= 1'b0;
        pcpi_rd    <= 32'd0;
        pcpi_ready <= 1'b0;
        pcpi_wait  <= 1'b0;          // popcount однотактна: чекати не треба
        if (is_ours) begin
            pcpi_rd    <= {26'd0, cnt};  // 6-бітний результат у 32-бітний rd
            pcpi_wr    <= 1'b1;          // так, пишемо в rd
            pcpi_ready <= 1'b1;          // готово вже цього такту
        end
    end
endmodule
