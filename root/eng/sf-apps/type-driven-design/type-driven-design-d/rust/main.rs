use std::marker::PhantomData;

struct Conn<S> { sock: Socket, _s: PhantomData<S> }   // S — стан, лише на рівні типів
struct Closed; struct Open; struct Authed;            // маркери-стани (порожні)

impl Conn<Closed> {
    fn connect(self) -> Conn<Open> { /* ... */ }       // Closed → Open
}
impl Conn<Open> {
    fn authenticate(self, key: &Key) -> Conn<Authed> { /* ... */ }   // Open → Authed
    fn close(self) -> Conn<Closed> { /* ... */ }
}
impl Conn<Authed> {
    fn request(&self, r: Req) -> Resp { /* ... */ }    // ЛИШЕ тут: слати можна лише автентифікованим
    fn close(self) -> Conn<Closed> { /* ... */ }
}
