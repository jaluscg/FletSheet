from flet_core.utils import is_asyncio, is_coroutine
import json

class SpecificEventHandler:
    def __init__(self, result_converter=None) -> None:
        self.__handlers = {}
        self.__result_converter = result_converter

    def get_sync_handler(self):
        return self.__sync_handler

    def get_handler(self):
        if is_asyncio():
            return self.__async_handler
        else:
            return self.__sync_handler

    def __sync_handler(self, e):
        print("se está ejecutando __sync_handler")
        for h in self.__handlers.keys():
            if self.__result_converter is not None:
                print(f"self.__result_converter {self.__result_converter} ")

                print(f"e.data en sync_handler: {e.data}")
                r = self.__result_converter(e)
                if r is not None:
                    print(f"r es self.__result_converter(e){r}")
                    r.target = e.target
                    r.name = e.name



                    r.data = e.data
                    r.control = e.control
                    r.page = e.page
                    h(r)
                    print(f"r.target: {r.target}, r.name: {r.name}, r.data: {r.data}, r.control: {r.control}, r.page: {r.page}")

            else:
                h(e)

    async def __async_handler(self, e):
        for h in self.__handlers.keys():
            if self.__result_converter is not None:
                r = self.__result_converter(e)
                if r is not None:
                    r.target = e.target
                    r.name = e.name
                    r.data = e.data
                    r.control = e.control
                    r.page = e.page
                    if is_coroutine(h):
                        await h(r)
                    else:
                        h(r)
            else:
                if is_coroutine(h):
                    await h(e)
                else:
                    h(e)

    def subscribe(self, handler):
        if handler is not None:
            self.__handlers[handler] = True

    def unsubscribe(self, handler):
        if handler in self.__handlers:
            self.__handlers.pop(handler)

    def count(self):
        return len(self.__handlers)