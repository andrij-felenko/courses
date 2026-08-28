    integer checks = 0;      // скільки звірок зробили (для звіту PASS)

    // ── ЕТАЛОН: рахує очікуване ТИМ САМИМ правилом, що DUT ──
    //    важливо: те саме <= і той самий фронт, що в дизайні,
    //    тож expected і count оновлюються синхронно, без off-by-one
    always @(posedge clk) begin
        if (rst)
            expected <= 4'd0;
        else if (en)
            expected <= expected + 4'd1;
        // інакше — тримає, як і DUT
    end

    // ── ЗВІРКА: після кожного фронту count має дорівнювати expected ──
    always @(posedge clk) begin
        // чекаємо, поки обидва защіпнуться (кінець кроку часу),
        // і аж тоді порівнюємо — #0 переносить нас у фазу ПІСЛЯ защіпки
        #0;
        if (count !== expected) begin
            $display("FAIL @ %0t: count=%b (%0d), чекали %b (%0d)",
                     $time, count, count, expected, expected);
            $finish;         // спиняємось на ПЕРШІЙ розбіжності
        end
        checks = checks + 1;
    end
