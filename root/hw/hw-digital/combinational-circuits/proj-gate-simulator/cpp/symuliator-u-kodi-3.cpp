int main() {
    printf("A B Cin | Sum Cout\n");
    for (int A = 0; A <= 1; ++A)
        for (int B = 0; B <= 1; ++B)
            for (int Cin = 0; Cin <= 1; ++Cin) {
                auto s = evaluate(adder, {{"A", A}, {"B", B}, {"Cin", Cin}});
                printf("%d %d  %d  |  %d    %d\n",
                       A, B, Cin, s.at("g3"), s.at("g5"));   // Sum=g3, Cout=g5
            }
}
