use std::marker::PhantomData;

// Стани протоколу — порожні типи-маркери. Даних нема; сенс лише в імені.
struct Closed;
struct Open;
struct Authed;

// Транспорт — заглушка. У житті тут TcpStream, UART, що завгодно.
struct Wire { peer: String, inbox: Vec<u8> }
impl Wire {
    fn dial(peer: &str) -> Wire { Wire { peer: peer.to_owned(), inbox: Vec::new() } }
    fn put(&mut self, bytes: &[u8]) { let _ = bytes; /* запис у канал */ }
    fn take(&mut self) -> Vec<u8> { std::mem::take(&mut self.inbox) }
}

struct AuthError;

// Хендл, параметризований СТАНОМ S.
// PhantomData<S> «вживає» параметр S, не займаючи ні байта в рантаймі.
struct Conn<S> { wire: Wire, _state: PhantomData<S> }

// Приватний перехід-помічник: перекласти транспорт у хендл іншого стану.
// НЕ pub — тільки методи нижче міняють стан, і лише за протоколом.
impl<S> Conn<S> {
    fn retag<T>(self) -> Conn<T> {
        Conn { wire: self.wire, _state: PhantomData }
    }
}

impl Conn<Closed> {
    fn new(peer: &str) -> Conn<Closed> {
        Conn { wire: Wire::dial(peer), _state: PhantomData }
    }
    fn open(self) -> Conn<Open> { self.retag() }        // Closed → Open
}

impl Conn<Open> {
    // Open → Authed. Споживає self; при відмові з'єднання згортається разом із ним.
    fn authenticate(mut self, key: &str) -> Result<Conn<Authed>, AuthError> {
        self.wire.put(key.as_bytes());
        if key.is_empty() { Err(AuthError) } else { Ok(self.retag()) }
    }
    fn close(self) -> Conn<Closed> { self.retag() }     // Open → Closed
}

impl Conn<Authed> {
    // ЛИШЕ тут. &mut self, а не self: у цьому стані можна слати БАГАТО запитів.
    fn request(&mut self, body: &str) -> Vec<u8> {
        self.wire.put(body.as_bytes());
        self.wire.take()
    }
    fn close(self) -> Conn<Closed> { self.retag() }     // Authed → Closed
}
