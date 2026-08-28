// серце FilterInputStream — те, з чого починається кожна обгортка java.io
public class FilterInputStream extends InputStream {
    protected volatile InputStream in;      // обгорнутий потік — ТИП КОМПОНЕНТА!

    protected FilterInputStream(InputStream in) {
        this.in = in;
    }

    public int read() throws IOException {
        return in.read();                    // просто передав униз
    }
    public int read(byte[] b, int off, int len) throws IOException {
        return in.read(b, off, len);         // просто передав униз
    }
    public void close() throws IOException {
        in.close();                          // просто передав униз
    }
    // ...так само skip(), available(), mark(), reset()
}
