def by_threat(reg):
    # спад експозиції, за рівної — важчий вплив вище; sorted стабільний → порядок ties сталий
    return sorted(reg, key=lambda r: (r.exposure, I_SCORE[r.impact]), reverse=True)


def lint(reg, today, stale_days=14):
    out = []
    for r in reg:
        if not r.active:                     # прийняте/закрите свідомо не чіпаємо
            continue
        idle = (today - r.reviewed).days
        if idle > stale_days:
            out.append((r.id, f"застій: {idle} дн. без перегляду (поріг {stale_days})"))
        if r.heavy:                          # важкий і відкритий → мусить мати тригер і власника
            if not r.trigger.strip():
                out.append((r.id, "важкий відкритий ризик без тригера"))
            if not r.owner.strip():
                out.append((r.id, "важкий відкритий ризик без власника"))
    return out


LABEL = {"open": "відкритий", "watching": "під наглядом",
         "accepted": "прийнято", "closed": "закритий"}


def report(reg, today) -> int:
    print(f"Реєстр Digital Homes — {len(reg)} рядків, станом на {today}\n")
    print("  експ  стан          рядок")
    for r in by_threat(reg):
        print(f"  {r.exposure:>4}  {LABEL[r.state]:<12}  {r.what}")
    problems = lint(reg, today)
    print("\nЛІНТЕР")
    if not problems:
        print("  чисто — жодного застояного чи напівпорожнього важкого рядка")
        return 0
    for rid, detail in problems:
        print(f"  ✗  {rid:<18} {detail}")
    print(f"\n{len(problems)} порушення → реєстр застоявся, CI падає")
    return 1


if __name__ == "__main__":
    # У CI today = date.today(); тут фіксуємо дату для відтворюваного прикладу.
    sys.exit(report(REGISTER, date(2026, 3, 24)))
