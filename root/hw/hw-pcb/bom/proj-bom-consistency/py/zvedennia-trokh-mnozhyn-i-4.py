def main(argv):
    if len(argv) < 4:
        print("вжиток: bomcheck <bom.csv> <schematic-refs.txt> <board-refs.txt>")
        return 2
    bom   = read_bom(argv[1])
    schem = read_ref_counts(argv[2])
    board = read_ref_counts(argv[3])

    problems = check_consistency(bom, schem, board)

    if problems == 0:
        print("OK: перелік компонентів узгоджений, можна відправляти")
        return 0
    print("ЗНАЙДЕНО ПРОБЛЕМ: %d — НЕ відправляти, доки не виправлено" % problems)
    return 1                        # ненульовий код спиняє конвеєр відправлення

if __name__ == "__main__":
    sys.exit(main(sys.argv))
