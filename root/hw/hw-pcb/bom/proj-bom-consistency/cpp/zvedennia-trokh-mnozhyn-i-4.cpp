int main(int argc, char** argv) {
    if (argc < 4) {
        printf("вжиток: bomcheck <bom.csv> <schematic-refs.txt> <board-refs.txt>\n");
        return 2;
    }
    std::vector<BomRow> bom = read_bom(argv[1]);
    std::unordered_map<std::string,int> schem = read_ref_counts(argv[2]);
    std::unordered_map<std::string,int> board = read_ref_counts(argv[3]);

    int problems = check_consistency(bom, schem, board);

    if (problems == 0) {
        printf("OK: перелік компонентів узгоджений, можна відправляти\n");
        return 0;
    }
    printf("ЗНАЙДЕНО ПРОБЛЕМ: %d — НЕ відправляти, доки не виправлено\n", problems);
    return 1;                       // ненульовий код спиняє конвеєр відправлення
}
