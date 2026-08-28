module alu_8bit (
    input  wire [7:0] a,
    input  wire [7:0] b,
    input  wire [3:0] opcode,
    output reg  [7:0] result,
    output wire       flag_z,
    output wire       flag_n,
    output reg        flag_c,
    output reg        flag_v
);

    // Коди операцій АЛУ
    localparam OP_ADD = 4'b0000;
    localparam OP_SUB = 4'b0001;
    localparam OP_AND = 4'b0010;
    localparam OP_OR  = 4'b0011;
    localparam OP_XOR = 4'b0100;
    localparam OP_NOT = 4'b0101;
    localparam OP_LSL = 4'b0110;
    localparam OP_LSR = 4'b0111;
    localparam OP_ASR = 4'b1000;

    // Внутрішні сигнали арифметичного тракту
    wire is_sub = (opcode == OP_SUB);
    wire [7:0] b_eff = b ^ {8{is_sub}};
    wire [7:0] g = a & b_eff;
    wire [7:0] p = a ^ b_eff;
    wire [8:0] c;

    // Ланцюжок паралельного переносу CLA
    assign c[0] = is_sub;
    assign c[1] = g[0] | (p[0] & c[0]);
    assign c[2] = g[1] | (p[1] & g[0]) | (p[1] & p[0] & c[0]);
    assign c[3] = g[2] | (p[2] & g[1]) | (p[2] & p[1] & g[0]) | (p[2] & p[1] & p[0] & c[0]);
    assign c[4] = g[3] | (p[3] & g[2]) | (p[3] & p[2] & g[1]) | (p[3] & p[2] & p[1] & g[0]) | (p[3] & p[2] & p[1] & p[0] & c[0]);
    assign c[5] = g[4] | (p[4] & c[4]);
    assign c[6] = g[5] | (p[5] & c[5]);
    assign c[7] = g[6] | (p[6] & c[6]);
    assign c[8] = g[7] | (p[7] & c[7]);

    wire [7:0] sum = p ^ c[7:0];

    // Мультиплексування результату та формування прапорців
    always @(*) begin
        flag_c = 1'b0;
        flag_v = 1'b0;
        case (opcode)
            OP_ADD, OP_SUB: begin
                result = sum;
                flag_c = c[8];
                flag_v = c[7] ^ c[8]; // Детектор V = Cin[7] ^ Cout[7]
            end
            OP_AND: result = a & b;
            OP_OR:  result = a | b;
            OP_XOR: result = a ^ b;
            OP_NOT: result = ~a;
            OP_LSL: begin
                flag_c = a[7];
                result = {a[6:0], 1'b0};
            end
            OP_LSR: begin
                flag_c = a[0];
                result = {1'b0, a[7:1]};
            end
            OP_ASR: begin
                flag_c = a[0];
                result = {a[7], a[7:1]};
            end
            default: result = 8'h00;
        endcase
    end

    // Прапорці Zero та Negative
    assign flag_z = (result == 8'h00);
    assign flag_n = result[7];

endmodule
