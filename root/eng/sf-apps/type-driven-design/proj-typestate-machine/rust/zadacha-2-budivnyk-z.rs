use std::marker::PhantomData;

struct Missing;   // поле ще не задано
struct Set;       // поле задано

struct RequestBuilder<U, M> {
    url: Option<String>,
    method: Option<String>,
    headers: Vec<(String, String)>,
    _u: PhantomData<U>,
    _m: PhantomData<M>,
}

impl RequestBuilder<Missing, Missing> {
    fn new() -> Self {
        RequestBuilder { url: None, method: None, headers: Vec::new(),
                         _u: PhantomData, _m: PhantomData }
    }
}

// url() існує, ЛИШЕ поки URL іще Missing: переставити двічі не вийде.
// M лишаємо яким був — метод це не чіпає.
impl<M> RequestBuilder<Missing, M> {
    fn url(self, u: &str) -> RequestBuilder<Set, M> {
        RequestBuilder { url: Some(u.to_owned()), method: self.method,
                         headers: self.headers, _u: PhantomData, _m: PhantomData }
    }
}

impl<U> RequestBuilder<U, Missing> {
    fn method(self, m: &str) -> RequestBuilder<U, Set> {
        RequestBuilder { url: self.url, method: Some(m.to_owned()),
                         headers: self.headers, _u: PhantomData, _m: PhantomData }
    }
}

// Необов'язкові поля доступні В БУДЬ-ЯКОМУ стані — прапорців не міняють.
impl<U, M> RequestBuilder<U, M> {
    fn header(mut self, k: &str, v: &str) -> Self {
        self.headers.push((k.to_owned(), v.to_owned()));
        self
    }
}

// send() існує ЛИШЕ у вершині <Set, Set>.
impl RequestBuilder<Set, Set> {
    fn send(self) -> String {
        let url = self.url.unwrap();        // <Set, _> — доказ, що тут Some
        let method = self.method.unwrap();  // <_, Set> — доказ, що тут Some
        format!("{method} {url} [{} заголовків]", self.headers.len())
    }
}
