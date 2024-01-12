import json
import time
from typing import Any, Optional

from flet_core.animation import AnimationCurve
from flet_core.control import Control, OptionalNumber
from flet_core.control_event import ControlEvent
from flet_core.event_handler import EventHandler
from flet_core.types import ScrollMode, ScrollModeString


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
            print("ejecutando convert_on_scroll_event_data")
            d = json.loads(e.data)
            return OnScrollEvent(**d)

        self.__on_scroll = EventHandler(convert_on_scroll_event_data)
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
        print("ejecutando scroll_to")
        total_data_rows = 1000  # Puede ser un valor fijo o la cantidad total de filas de tus datos de Excel

        # Ajustar el offset si es necesario
        if offset is not None:
            # Asegurarse de que el offset esté dentro del rango de datos disponibles
            offset = max(0, min(offset, total_data_rows - 1))

        # Crear el mensaje para la función de desplazamiento
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

        # Establecer los atributos y actualizar el control
        self._set_attr_json("method", m)
        self.update()

    async def scroll_to_async(
        self,
        offset: Optional[float] = None,
        delta: Optional[float] = None,
        key: Optional[str] = None,
        duration: Optional[int] = None,
        curve: Optional[AnimationCurve] = None,
    ):
        
        print("ejecutando scroll_to_async")
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
        self._set_attr_json("method", m)
        await self.update_async()

    # scroll
    @property
    def scroll(self) -> Optional[ScrollMode]:
        print("ejecturando @property def scroll")
        return self.__scroll

    @scroll.setter
    def scroll(self, value: Optional[ScrollMode]):
        print("ejecutando @scroll.setter def scroll")
        self.__scroll = value
        if isinstance(value, ScrollMode):
            self._set_attr("scroll", value.value)
        else:
            self.__set_scroll(value)

    def __set_scroll(self, value: Optional[ScrollModeString]):
        print("ejecutando _set_scroll")
        if value is True:
            value = "auto"
        elif value is False:
            value = None
        self._set_attr("scroll", value)

    # auto_scroll
    @property
    def auto_scroll(self) -> Optional[str]:
        print("ejecutando @propertu def auto_scroll")
        return self._get_attr("autoScroll", data_type="bool", def_value=False)

    @auto_scroll.setter
    def auto_scroll(self, value: Optional[bool]):
        print("ejecutando @auto_scroll.setter def auto_scroll")
        self._set_attr("autoScroll", value)

    # reverse
    @property
    def reverse(self) -> Optional[bool]:
        print("ejecutando @property def reverse")
        return self._get_attr("reverse", data_type="bool", def_value=False)

    @reverse.setter
    def reverse(self, value: Optional[bool]):
        print("ejecutando @reverse.setter def reverse")
        self._set_attr("reverse", value)

    # on_scroll_interval
    @property
    def on_scroll_interval(self) -> OptionalNumber:
        print("ejecutando @property def on_scroll_interval")
        return self._get_attr("onScrollInterval")

    @on_scroll_interval.setter
    def on_scroll_interval(self, value: OptionalNumber):
        print("ejectuando @on_scoll_interval.setter def on_scroll_interval")
        self._set_attr("onScrollInterval", value)

    # on_scroll
    @property
    def on_scroll(self):
        print("ejectuando #on_scoll @property def on_scroll")
        return self.__on_scroll

    @on_scroll.setter
    def on_scroll(self, handler):
        print("ejecutando @on_scroll.setter def on_scroll")
        
        print("ejecutando wrapped-handler")
        # Calcula el cambio en filas y columnas basado en el desplazamiento
        delta_rows = int(self.scroll_delta / self.cell_height)
        delta_cols = int(self.scroll_delta / self.cell_width)

        # Actualiza las filas y columnas visibles
        self.visible_start_row = max(0, self.visible_start_row + delta_rows)
        self.visible_end_row = min(self.ROWS, self.visible_start_row + 12)
            
        self.visible_start_col = max(0, self.visible_start_col + delta_cols)
        self.visible_end_col = min(self.COLS, self.visible_start_col + 10)

        # Actualiza las celdas visibles y sus índices
        self.update_visible_cells()
        self.update_indices()

    

    def update_view_with_excel_data(self):
        # Aquí debes implementar la lógica para actualizar las celdas visibles
        # basadas en visible_start_row y visible_end_row
        print("ejecutandose update_view_with_excel")
        pass


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

    def __str__(self):
        print(f"ejecutando class OnScrollEvent {self.event_type}: pixels={self.pixels}, min_scroll_extent={self.min_scroll_extent}, max_scroll_extent={self.max_scroll_extent}, viewport_dimension={self.viewport_dimension}, scroll_delta={self.scroll_delta}, direction={self.direction}, overscroll={self.overscroll}, velocity={self.velocity}")
        return f"{self.event_type}: pixels={self.pixels}, min_scroll_extent={self.min_scroll_extent}, max_scroll_extent={self.max_scroll_extent}, viewport_dimension={self.viewport_dimension}, scroll_delta={self.scroll_delta}, direction={self.direction}, overscroll={self.overscroll}, velocity={self.velocity}"