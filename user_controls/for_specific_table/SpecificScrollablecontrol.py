import json
import time
from typing import Any, Optional

from flet_core.animation import AnimationCurve
from flet_core.control import Control, OptionalNumber
from flet_core.control_event import ControlEvent
from flet_core.types import ScrollMode, ScrollModeString

from.SpecificEventHandler import SpecificEventHandler

class SpecificScrollableControl(Control):
    def __init__(
        self,
        scroll: Optional[ScrollMode] = None,
        auto_scroll: Optional[bool] = None,
        reverse: Optional[bool] = None,
        on_scroll_interval: OptionalNumber = None,
        on_scroll: Any = None,
    ):
        def convert_on_scroll_event_data(e):
            print(f"e.data = {e.data}")
            d = json.loads(e.data)
            # Modificar el valor de 'maxse'
            #d['maxse'] = 2000
            #d['vd'] = 3000
            # Serializar el diccionario modificado de vuelta a una cadena JSON
            #e.data = json.dumps(d)
            #print(f"nueva e.data = {e.data}")


            print(f"ejecutando convert_on_scroll_event_data {d}")
            return OnScrollEvent(**d)

        self.__on_scroll = SpecificEventHandler(convert_on_scroll_event_data)
        print(f"self.__on_scroll{self.__on_scroll}")

        self._add_event_handler("onScroll", self.__on_scroll.get_handler())

        self.scroll = scroll
        self.auto_scroll = auto_scroll
        self.reverse = reverse
        self.on_scroll_interval = on_scroll_interval
        self.on_scroll = on_scroll

    def scroll_to(
        self,
        offset: Optional[float] = None,
        delta: Optional[float] = None,
        key: Optional[str] = None,
        duration: Optional[int] = None,
        curve: Optional[AnimationCurve] = None,
    ):
        m = {
            "n": "scroll_to",
            "i": str(time.time()),
            "p": {
                "offset": offset,
                "delta": delta,
                "key": key,
                "duration": duration,
                "curve": curve.value if curve is not None else None,
            },
        }
        print(f"ejecutando scroll_to {m}")
        self._set_attr_json("method", m)
        print(f"self._set_attr_json: {self._set_attr_json}")
        self.update()

    async def scroll_to_async(
        self,
        offset: Optional[float] = None,
        delta: Optional[float] = None,
        key: Optional[str] = None,
        duration: Optional[int] = None,
        curve: Optional[AnimationCurve] = None,
    ):
        m = {
            "n": "scroll_to",
            "i": str(time.time()),
            "p": {
                "offset": offset,
                "delta": delta,
                "key": key,
                "duration": duration,
                "curve": curve.value if curve is not None else None,
            },
        }
        print(f"ejecutando scrol_to_async {m}")
        self._set_attr_json("method", m)
        print(f"self._set_attr_json: {self._set_attr_json}")
        await self.update_async()

    # scroll
    @property
    def scroll(self) -> Optional[ScrollMode]:
        print("ejecutando @property def scroll")
        return self.__scroll

    @scroll.setter
    def scroll(self, value: Optional[ScrollMode]):
        self.__scroll = value
        if isinstance(value, ScrollMode):
            print("ejecutando @scroll.setter def scroll if isinstance")
            print(f"value: {value}")
            self._set_attr("scroll", value.value)
            print(f"self._set_attr: {self._set_attr}")
        else:
            print("ejecutando @scroll.setter def scroll else")
            self.__set_scroll(value)

    def __set_scroll(self, value: Optional[ScrollModeString]):
        if value is True:
            print("ejecutando def __set_scroll value True")
            value = "auto"
        elif value is False:
            print("ejecutando def __set_scroll value False")
            value = None
        self._set_attr("scroll", value)
        self.set_attr("max_setter_scroll", 2000)
        print(f"self._set_attr: {self._set_attr}")

    # auto_scroll
    @property
    def auto_scroll(self) -> Optional[str]:
        print("ejecutando @property def auto_scroll")
        
        return self._get_attr("autoScroll", data_type="bool", def_value=False)

    @auto_scroll.setter
    def auto_scroll(self, value: Optional[bool]):
        print("ejecutando @auto_scroll.setter def auto_scroll")
        self._set_attr("autoScroll", value)
        self._set_attr("maxse", 2000)
        print(f"self._set_attr: {self._set_attr}")

    # reverse
    @property
    def reverse(self) -> Optional[bool]:
        print("ejecutando @property def reverse")
        return self._get_attr("reverse", data_type="bool", def_value=False)

    @reverse.setter
    def reverse(self, value: Optional[bool]):
        print("ejecutando @reverse.setter def reverse")
        self._set_attr("reverse", value)
        print(f"self._set_attr: {self._set_attr}")

    # on_scroll_interval
    @property
    def on_scroll_interval(self) -> OptionalNumber:
        print("ejecutando @property def on_scroll_interval")
        return self._get_attr("onScrollInterval")

    @on_scroll_interval.setter
    def on_scroll_interval(self, value: OptionalNumber):
        print("ejecutando @on_scroll_interval.setter def on_scroll_interval")
        self._set_attr("onScrollInterval", value)
        print(f"self._set_attr: {self._set_attr}")

    # on_scroll
    @property
    def on_scroll(self):
        print("ejecutando @property def on_Scroll")
        return self.__on_scroll

    @on_scroll.setter
    def on_scroll(self, handler):
        print("ejecutando @on_scroll.setter def on_scroll")
        self.__on_scroll.subscribe(handler)
        self._set_attr("onScroll", True if handler is not None else None)
        print(f"self._set_attr: {self._set_attr}")


class OnScrollEvent(ControlEvent):
    def __init__(
        self, t, p, minse, maxse, vd, sd=None, dir=None, os=None, v=None
    ) -> None:
        self.event_type: str = t
        self.pixels: float = p
        self.min_scroll_extent: float = minse
        self.max_scroll_extent: float = maxse
        self.viewport_dimension: float = vd
        self.scroll_delta: Optional[float] = sd
        self.direction: Optional[str] = dir
        self.overscroll: Optional[float] = os
        self.velocity: Optional[float] = v
        print(f"{self.event_type}: pixels={self.pixels}, min_scroll_extent={self.min_scroll_extent}, max_scroll_extent={self.max_scroll_extent}, viewport_dimension={self.viewport_dimension}, scroll_delta={self.scroll_delta}, direction={self.direction}, overscroll={self.overscroll}, velocity={self.velocity}")

    def __str__(self):
        print("Ejecutando clase OnScrollEvent def __str__")
        return f"{self.event_type}: pixels={self.pixels}, min_scroll_extent={self.min_scroll_extent}, max_scroll_extent={self.max_scroll_extent}, viewport_dimension={self.viewport_dimension}, scroll_delta={self.scroll_delta}, direction={self.direction}, overscroll={self.overscroll}, velocity={self.velocity}"