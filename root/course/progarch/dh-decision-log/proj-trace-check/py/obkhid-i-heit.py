def main() -> int:
    adrs = load_adrs(ADR_DIR)
    breaks = (check_dangling_refs(adrs, REPO)
              + check_orphans(adrs, REPO)
              + check_chains(adrs)
              + check_radio_guard(REPO))
    print(f"Слід рішень DH — {len(adrs)} ADR, чотири перевірки\n")
    if not breaks:
        print("  слід цілий: посилання ведуть кудись, ухвалені прив'язані, ланцюги без циклів")
        return 0
    for b in sorted(breaks, key=lambda x: (x.adr, x.detail)):
        print(f"  ✗  {b.adr}  {b.detail}")
    print(f"\n{len(breaks)} розрив(ів) сліду → CI падає")
    return 1


if __name__ == "__main__":
    sys.exit(main())
