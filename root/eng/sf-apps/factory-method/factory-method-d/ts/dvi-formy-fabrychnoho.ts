class Application {
  // фабричний метод зі СТАНДАРТОМ — базу можна вживати без нащадків
  protected createDocument(): Document {
    return new PlainTextDocument();   // розумний типовий продукт
  }
  newDocument(): Document {
    const doc = this.createDocument();
    doc.open();
    return doc;
  }
}

class DrawingApp extends Application {
  protected createDocument(): Document {   // перевизначаємо ЛИШЕ там, де треба
    return new DrawingDocument();
  }
}
