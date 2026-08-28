public interface XMLStreamReader extends XMLStreamConstants {
    // Рух курсора
    int     next() throws XMLStreamException;
    void    require(int type, String namespaceURI, String localName) throws XMLStreamException;
    String  getElementText() throws XMLStreamException;
    int     nextTag() throws XMLStreamException;
    boolean hasNext() throws XMLStreamException;
    void    close() throws XMLStreamException;

    // Властивості поточного елемента
    String  getNamespaceURI();
    String  getLocalName();
    String  getPrefix();
    boolean hasName();
    QName   getName();

    // Доступ до атрибутів поточного елемента
    int     getAttributeCount();
    String  getAttributeNamespace(int index);
    String  getAttributeLocalName(int index);
    String  getAttributePrefix(int index);
    String  getAttributeType(int index);
    String  getAttributeValue(int index);
    String  getAttributeValue(String namespaceURI, String localName);
    boolean isAttributeSpecified(int index);

    // Доступ до просторів імен
    int     getNamespaceCount();
    String  getNamespacePrefix(int index);
    String  getNamespaceURI(int index);

    // Доступ до текстового вмісту
    char[]  getTextCharacters();
    int     getTextCharacters(int sourceStart, char[] target, int targetStart, int length) throws XMLStreamException;
    int     getTextStart();
    int     getTextLength();
    String  getText();
    boolean hasText();

    // Діагностика локації у потоці
    Location getLocation();
    int      getEventType();
}
