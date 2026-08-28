// Віддати файл name із файлової системи, порціями через io.Copy.
var types = map[string]string{
    ".html": "text/html", ".css": "text/css",
    ".js": "application/javascript",
}

func sendFileFromFS(w http.ResponseWriter, name string) {
    full := filepath.Join("/spiffs", name)
    f, err := os.Open(full)
    if err != nil { // нема файлу — чесний 404
        http.Error(w, "not found", http.StatusNotFound)
        return
    }
    defer f.Close()

    ctype, ok := types[filepath.Ext(name)] // тип за розширенням
    if !ok {
        ctype = "text/plain"
    }
    w.Header().Set("Content-Type", ctype)

    // ПОРЦІЯМИ: io.Copy жене файл шматками, не тримаючи його в пам'яті цілком
    io.Copy(w, f)
}
