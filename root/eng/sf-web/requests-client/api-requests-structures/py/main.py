class Session:
    def request(
        self,
        method: str,
        url: str,
        params: Optional[Union[Dict[str, Any], List[Tuple[str, Any]], bytes]] = None,
        data: Optional[Union[Dict[str, Any], List[Tuple[str, Any]], bytes, IO]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Union[Dict[str, str], CookieJar]] = None,
        files: Optional[Dict[str, Any]] = None,
        auth: Optional[Union[Tuple[str, str], AuthBase, Callable]] = None,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
        allow_redirects: bool = True,
        proxies: Optional[Dict[str, str]] = None,
        hooks: Optional[Dict[str, List[Callable]]] = None,
        stream: Optional[bool] = None,
        verify: Optional[Union[bool, str]] = None,
        cert: Optional[Union[str, Tuple[str, str]]] = None,
        json: Optional[Any] = None,
    ) -> Response:
        ...

    def prepare_request(self, request: Request) -> PreparedRequest:
        ...

    def send(self, request: PreparedRequest, **kwargs: Any) -> Response:
        ...

    def mount(self, prefix: str, adapter: BaseAdapter) -> None:
        ...

    def close(self) -> None:
        ...
