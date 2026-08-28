def blocks_commit(reg: list[Assumption]) -> list[Assumption]:
    """Несучі припущення незворотного кроку, ще не зняті перевіркою."""
    return [a for a in ranked(reg) if a.irreversible and a.worth_checking()]


def gate(reg: list[Assumption]) -> None:
    blockers = blocks_commit(reg)
    if blockers:
        lines = "\n".join(
            f"  ✗ {a.id}: {a.claim} "
            f"(очік. втрата {a.expected_loss():.0f}, перевірка {a.cost_to_check:.0f})"
            for a in blockers)
        raise SystemExit(
            "НЕЗВОРОТНИЙ КРОК ЗАБЛОКОВАНО — спершу зніми перевіркою:\n" + lines)
    print("гейт відкрито: усі несучі припущення незворотного кроку зняті")


if __name__ == "__main__":
    gate(load("assumptions.yml"))     # у CI перед заливкою прошивки в поле
