abstract class Application {
  // фабричний метод: КАРКАС не знає конкретного класу, лишає діру для нащадка
  protected abstract createDocument(): Document;

  newDocument(): Document {                 // спільна логіка каркаса
    const doc = this.createDocument();      // ...кличе діру...
    doc.open();
    this.registerInRecent(doc);
    return doc;
  }
  private registerInRecent(doc: Document) { /* ... */ }
}

class DrawingApp extends Application {
  protected createDocument(): Document {    // нащадок ОБИРАЄ клас
    return new DrawingDocument();
  }
}
class SpreadsheetApp extends Application {
  protected createDocument(): Document {
    return new SpreadsheetDocument();
  }
}
