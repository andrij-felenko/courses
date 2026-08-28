enum Link { Open(Conn<Open>), Authed(Conn<Authed>) }

fn from_config(secure: bool, key: &str, c: Conn<Open>) -> Link {
    if secure {
        c.authenticate(key).map(Link::Authed).unwrap_or_else(|_| todo!())
    } else {
        Link::Open(c)
    }
}
// далі — match по Link; гілка Authed має request, гілка Open — ні.
