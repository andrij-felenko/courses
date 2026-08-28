func Bump(v, kind string) string {
    var maj, min, pat int
    fmt.Sscanf(v, "%d.%d.%d", &maj, &min, &pat)
    switch kind {
    case "major":
        return fmt.Sprintf("%d.0.0", maj+1)      // скидає min і pat
    case "minor":
        return fmt.Sprintf("%d.%d.0", maj, min+1) // скидає pat
    default:
        return fmt.Sprintf("%d.%d.%d", maj, min, pat+1)
    }
}
