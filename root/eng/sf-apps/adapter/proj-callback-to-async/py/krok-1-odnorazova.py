import asyncio

def read_file_async(path):
    loop = asyncio.get_running_loop()
    fut = loop.create_future()          # порожній «проміс»

    def on_done(err, data):             # старий колбек
        if err:
            fut.set_exception(err)      # → reject
        else:
            fut.set_result(data)        # → resolve

    legacy_read(path, on_done)          # чужа колбекова функція
    return fut                          # це awaitable

data = await read_file_async("./config.json")
