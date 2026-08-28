template <typename OnAccept, typename OnOOD, typename OnAmbiguous>
void match_decision(
    const SelectiveOutput& res,
    OnAccept&& on_accept,
    OnOOD&& on_ood,
    OnAmbiguous&& on_ambiguous
) {
    switch (res.status) {
        case DecisionStatus::Accepted:
            std::forward<OnAccept>(on_accept)(res.predicted_class, res.confidence);
            break;
        case DecisionStatus::RejectOOD:
            std::forward<OnOOD>(on_ood)(res.free_energy);
            break;
        case DecisionStatus::RejectAmbiguous:
            std::forward<OnAmbiguous>(on_ambiguous)(res.normalized_entropy);
            break;
    }
}
