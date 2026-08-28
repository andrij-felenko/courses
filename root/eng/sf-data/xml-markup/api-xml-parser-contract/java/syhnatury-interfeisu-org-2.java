public interface Attributes {
    int getLength();
    String getURI(int index);
    String getLocalName(int index);
    String getQName(int index);
    String getType(int index);       // "CDATA", "ID", "IDREF", "NMTOKEN" тощо
    String getValue(int index);

    int getIndex(String uri, String localName);
    int getIndex(String qName);
    String getType(String uri, String localName);
    String getValue(String uri, String localName);
    String getValue(String qName);
}
