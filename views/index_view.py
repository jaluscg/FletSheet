import flet as ft
from flet import *
import os
import json


class IndexView:
    def __init__(self):
        ...

    

    def view(self,page:ft.page):


        return  ft.View(
            "/",
            controls=[

                ft.SafeArea(
                    
                    content=

                        Row(
                            
                            controls=[
                                TextButton(text="Entrar a FletSheet", icon= icons.APP_REGISTRATION_SHARP, on_click=lambda _: page.go("/menu")),
                            ],
                            spacing=50,
                            alignment="center",

                        )
                     
                )
            ],
        

            vertical_alignment =  MainAxisAlignment.CENTER, 
            horizontal_alignment = CrossAxisAlignment.CENTER, 
          
        )