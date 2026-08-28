// Присвоїти літералові L значення «істина» й спростити формулу:
//   клаузу з L викидаємо (задоволена); з решти прибираємо ¬L (хибний літерал).
// Порожня клауза → конфлікт (через out-параметр).
CNF assign(const CNF& F, Lit L, bool& conflict) {
    CNF out;
    out.reserve(F.size());
    for (const Clause& c : F) {
        bool satisfied = false;
        Clause reduced;
        for (Lit m : c) {
            if (m ==  L) { satisfied = true; break; }   // істинний літерал → клауза знята
            if (m == -L) continue;                       // хибний літерал → викинути
            reduced.push_back(m);
        }
        if (satisfied) continue;
        if (reduced.empty()) { conflict = true; return out; }   // порожня клауза → суперечність
        out.push_back(std::move(reduced));
    }
    return out;
}
