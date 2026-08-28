if __name__ == "__main__":
    xs = simulate()
    plan_mode = sum(m for _, o, m, p in TASKS)                    # наївний план на моди
    sum_pess  = sum(p for _, o, m, p in TASKS) + sum(e for *_, e in SCHED_RISKS)
    p80 = pct(xs, 80)

    print(f"Σ мод (наївний план):      {plan_mode:.0f} днів")
    print(f"середнє E (сподіване):     {sum(xs) / len(xs):.1f} днів")
    print(f"P80 (беремо в зобов'язання):{p80:.0f} днів")
    print(f"Σ песимістичних:           {sum_pess:.0f} днів")
    print(f"чесний резерв = P80 − план = {p80 - plan_mode:.0f} днів")
