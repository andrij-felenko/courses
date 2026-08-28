// Плагін: реалізує контракт і більше нічого про ядро не знає.
type MarkdownExporter struct{}

func (MarkdownExporter) Extension() string { return "md" }
func (MarkdownExporter) Export(doc Document) []byte {
    var b strings.Builder
    for _, bl := range doc.Blocks {
        fmt.Fprintf(&b, "# %s\n\n%s\n\n", bl.Title, bl.Body)
    }
    return []byte(b.String())
}
