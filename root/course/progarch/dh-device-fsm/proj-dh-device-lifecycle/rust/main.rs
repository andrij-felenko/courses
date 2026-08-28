// Стани — типи-маркери; хендл параметризований станом. Даних стану тут не тримаємо.
use std::marker::PhantomData;
struct New; struct Online; struct Offline; struct Retired;

struct Device<S> { id: String, home: Option<String>, _s: PhantomData<S> }

impl Device<New> {
    fn unpack(id: &str) -> Device<New> {
        Device { id: id.into(), home: None, _s: PhantomData }
    }
    fn commission(self, home: &str) -> Device<Online> {         // new → online
        Device { id: self.id, home: Some(home.into()), _s: PhantomData }
    }
}
impl Device<Online> {
    fn mark_offline(self) -> Device<Offline> { self.retag() }   // online → offline
    fn retire(self)       -> Device<Retired> { self.retag() }   // online → retired
}
impl Device<Offline> {
    fn mark_online(self) -> Device<Online>  { self.retag() }    // offline → online
    fn retire(self)      -> Device<Retired> { self.retag() }    // offline → retired
}
// Device<Retired> не має ЖОДНОГО методу — кінець, забезпечений компілятором.

impl<S> Device<S> {                          // приватний помічник; НЕ pub — це замок
    fn retag<T>(self) -> Device<T> {
        Device { id: self.id, home: self.home, _s: PhantomData }
    }
}
