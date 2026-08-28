type ExportRegistry struct {
    byExt map[string]Exporter
}

func NewExportRegistry() *ExportRegistry {
    return &ExportRegistry{byExt: map[string]Exporter{}}
}

func (r *ExportRegistry) Register(e Exporter) { // сюди плагін кладе себе
    r.byExt[e.Extension()] = e
}

func (r *ExportRegistry) ExportAs(ext string, doc Document) ([]byte, error) {
    e, ok := r.byExt[ext]                       // ядро бере плагін за ключем
    if !ok {
        return nil, fmt.Errorf("немає плагіна для .%s", ext)
    }
    return e.Export(doc), nil                    // і гукає через контракт
}
