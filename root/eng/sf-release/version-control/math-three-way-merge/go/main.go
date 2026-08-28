type Verdict int

const (
    TakeBase Verdict = iota
    TakeOurs
    TakeTheirs
    Conflict
)

// base, ours, theirs — три версії одного рядка (порівнюємо як рядки)
func decideLine(base, ours, theirs string) Verdict {
    oursChanged := ours != base     // наше рухалося?
    theirsChanged := theirs != base // їхнє рухалося?

    switch {
    case !oursChanged && !theirsChanged:
        return TakeBase   // випадок 1
    case oursChanged && !theirsChanged:
        return TakeOurs   // випадок 2
    case !oursChanged && theirsChanged:
        return TakeTheirs // випадок 2 (дзеркало)
    }

    // тут обидва рухалися:
    if ours == theirs {
        return TakeOurs // випадок 3: збіглися → одне значення
    }
    return Conflict // випадок 4: розійшлися
}
