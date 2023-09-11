import flet as ft
from flet import *
from flet_route import Params,Basket


class IndexView:
    def __init__(self):
        ...

    def view(self,page:ft.page,params:Params,basket:Basket):
        print(params)
        print(basket)


        return ft.View(
            "/",
            controls=[


                        Row(
                            
                            controls=[
                                TextButton(text="Entrar a FletSheet", icon= icons.APP_REGISTRATION_SHARP, on_click=lambda _: page.go("/menu")),
                            ],
                            spacing=50,
                            alignment="center",

                        )
                     
                    
            ],

            vertical_alignment =  MainAxisAlignment.CENTER, 
            horizontal_alignment = CrossAxisAlignment.CENTER, 
          
        )
