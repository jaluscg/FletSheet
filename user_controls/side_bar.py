import flet as ft
from flet import *
class ModernNavBar(UserControl):
    def __init__(self,func,func1,func2,func3,func4,func5,func6,func7):
        self.func = func
        self.func1 = func1
        self.func2 = func2
        self.func3 = func3
        self.func4 = func4
        self.func5 = func5
        self.func6 = func6
        self.func7 = func7
        super().__init__()

    def HighlightContainer(self, e):
        if e.data == "true":
            e.control.bgcolor = "white10"
            e.control.update()

            e.control.content.controls[0].icon_color = "white"
            e.control.content.controls[1].color = "white"
            e.control.content.update()
        else:
            e.control.bgcolor = None
            e.control.update()

            e.control.content.controls[0].icon_color = "#cccccc"
            e.control.content.controls[1].color = "#cccccc"
            e.control.content.update()

    def UserData(self, initials: str, name: str, description: str):
        return Container(
            content=Row(
                controls=[
                    Container(
                        width=42,
                        height=50,
                        border_radius=8,
                        bgcolor="bluegrey900",
                        alignment=alignment.center,
                        content=Text(
                            value=initials,
                            size=20,
                            weight="bold",
                        ),
                        
                    ),
                    Column(
                        spacing=1,
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            Text(
                                value=name,
                                size=15,
                                weight="bold",
                                opacity=1,
                                animate_opacity=200,
                            ),
                            Text(
                                value=description,
                                size=12,
                                weight="w400",
                                color="#cccccc",
                                opacity=1,
                                animate_opacity=200,
                            ),
                        ],
                    ),
                ]
            )
        )

    def ContainedIcon(self, icon_name, text,on_click):

        return Container(
            width=180,
            height=45,
            border_radius=10,
            on_hover=lambda e: self.HighlightContainer(e),
            ink=True,
            expand=True,
            on_click=on_click,
            content=Row(
                controls=[
                    IconButton(
                        icon=icon_name,
                        icon_size=23,
                        icon_color="#cccccc",
                        selected=False,
                        style=ButtonStyle(
                            shape={
                                "": RoundedRectangleBorder(radius=7),
                            },
                            overlay_color={"": "transparent"},
                        )
                    ),
                    Text(
                        value=text,
                        color="#cccccc",
                        size=14,
                        opacity=1,
                        animate_opacity=200,
                    ),
                ],
            ),
        )

    def build(self):

        return Container(
            width=200,
            height=580,
            padding=padding.only(top=10),
            alignment=alignment.center,
            content=Column(
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment="center",
                controls=[
                    self.UserData("LI", "Line Indent", "Softeware Engineer"),
                    Divider(height=5, color="transparent"),
                    self.ContainedIcon(icons.SEARCH, "Search", self.func),
                    self.ContainedIcon(icons.DASHBOARD_ROUNDED, "Dashboard", self.func1),
                    self.ContainedIcon(icons.BAR_CHART, "Revenue", self.func2),
                    self.ContainedIcon(icons.NOTIFICATIONS, "Notifications", self.func3),
                    self.ContainedIcon(icons.PIE_CHART_ROUNDED, "Analytics", self.func4),
                    self.ContainedIcon(icons.FAVORITE_ROUNDED, "Likes", self.func5),
                    self.ContainedIcon(icons.SETTINGS, "Settings", self.func6),
                    Divider(height=5, color="white24"),
                    self.ContainedIcon(icons.LOGOUT_ROUNDED, "Logout", self.func7),
                ],
            ),
        )

def SideBar(page,btn_1,btn_2,btn_3,btn_4,btn_5,btn_6,btn_7,btn_8):
    

    SideBar = Container(
            width=200,
            height=page.window_height*2,
            animate=animation.Animation(500, "decelerate"),
            bgcolor="#272726",
            border_radius=5,
            padding=10,
            content=ModernNavBar(btn_1,btn_2,btn_3,btn_4,btn_5,btn_6,btn_7,btn_8)
        )


    return SideBar
