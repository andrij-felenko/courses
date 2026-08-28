public interface ContentHandler {
    // Керування життєвим циклом документа
    void setDocumentLocator(Locator locator);
    void startDocument() throws SAXException;
    void endDocument() throws SAXException;

    // Зв'язування та розрив префіксів просторів імен
    void startPrefixMapping(String prefix, String uri) throws SAXException;
    void endPrefixMapping(String prefix) throws SAXException;

    // Обробка тегів і тексту
    void startElement(String uri, String localName, String qName, Attributes atts) throws SAXException;
    void endElement(String uri, String localName, String qName) throws SAXException;
    void characters(char[] ch, int start, int length) throws SAXException;
    void ignorableWhitespace(char[] ch, int start, int length) throws SAXException;

    // Додаткові метадані
    void processingInstruction(String target, String data) throws SAXException;
    void skippedEntity(String name) throws SAXException;
}
