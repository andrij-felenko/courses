enum class Verdict { TakeBase, TakeOurs, TakeTheirs, Conflict };

// base, ours, theirs — три версії одного рядка (порівнюємо як рядки)
Verdict decide_line(std::string_view base,
                    std::string_view ours,
                    std::string_view theirs)
{
    bool ours_changed   = ours   != base;   // наше рухалося?
    bool theirs_changed = theirs != base;   // їхнє рухалося?

    if (!ours_changed && !theirs_changed) return Verdict::TakeBase;   // випадок 1
    if ( ours_changed && !theirs_changed) return Verdict::TakeOurs;   // випадок 2
    if (!ours_changed &&  theirs_changed) return Verdict::TakeTheirs; // випадок 2 (дзеркало)

    // тут обидва рухалися:
    if (ours == theirs) return Verdict::TakeOurs;  // випадок 3: збіглися → одне значення
    return Verdict::Conflict;                      // випадок 4: розійшлися
}
