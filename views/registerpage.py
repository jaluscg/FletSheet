import flet as ft
from flet import *
from flet_route import Params,Basket
from flet_runtime.auth.oauth_provider import OAuthProvider
from typing import Optional, Callable

import pyrebase
import datetime

from flet_runtime.auth.providers.google_oauth_provider import GoogleOAuthProvider
import os

class RegisterView:
    def __init__(self):
        ...




    def InputTextField(self, text:str, hide:bool):
                    return Container(
                        alignment=alignment.center,
                        content=TextField(
                            height=48,
                            width=255,
                            bgcolor="#f0f3f6",
                            text_size=12,
                            color="black",
                            border_color="transparent",
                            hint_text=text,
                            filled=True,
                            cursor_color="black",
                            hint_style=TextStyle(
                                size=11,
                                color="black",
                            ),
                            password=hide, #para colocar true o false en caso de que sea un campo de contraseña

                        )
                    )

    def SignInOptions(self, path:str, name:str, click: Optional[Callable] = None):
        return Container(
            content=ElevatedButton(
                content=Row(
                    alignment="center",
                    spacing=4,
                    controls=[
                        Image(
                            src=path, #path es la ruta de la imagen
                            width=30,
                            height=30,
                        ),
                        Text(
                            name, #Nombre de la plataforma a iniciar
                            color="black",
                            size=10,
                            weight="bold",
                        ),

                    ],
                ),

                    width=255,

                    style=ButtonStyle(
                         shape={ "": RoundedRectangleBorder(radius=8), }
                    ),

                    bgcolor={
                        "": "#f0f3f6"
                    },

                    on_click= click,
                ),
            )


    


           
    
    def view(self,page:ft.page,params:Params,basket:Basket):
        print(params)
        print(basket)

        
        def _register_user(email, password):

            config = {
            "apiKey": "AIzaSyDscDBF-ytR_6B63va3r_I7jlcKZ8AYBXU",
            "authDomain": "scan-magico-ee23e.firebaseapp.com",
            "databaseURL": "",
            "projectId": "scan-magico-ee23e",
            "storageBucket": "scan-magico-ee23e.appspot.com",
            "messagingSenderId": "945696136373",
            "appId": "1:945696136373:web:a43030f77f15e859fbb2fc",
            "measurementId": "G-7JF44CXYRT"
            }
        
            firebase = pyrebase.initialize_app(config)

            auth = firebase.auth()



            try:
                auth.create_user_with_email_and_password(email, password)
                print("Usuario registrado")
                page.go("/menu")

        
            except Exception as e:
                print(e)
                page.go("/menu")



                
                


        
        emailseccion = TextField(
                            height=48,
                            width=255,
                            bgcolor="#f0f3f6",
                            text_size=12,
                            color="black",
                            border_color="transparent",
                            hint_text="Email",
                            filled=True,
                            cursor_color="black",
                            hint_style=TextStyle(
                                size=11,
                                color="black",
                            ),
                            password=False, #para colocar true o false en caso de que sea un campo de contraseña

                        )

        contraseccion = TextField(
                            height=48,
                            width=255,
                            bgcolor="#f0f3f6",
                            text_size=12,
                            color="black",
                            border_color="transparent",
                            hint_text="Contraseña",
                            filled=True,
                            cursor_color="black",
                            hint_style=TextStyle(
                                size=11,
                                color="black",
                            ),
                            password=True, #para colocar true o false en caso de que sea un campo de contraseña

                        )




        def login_google(e):
            provider = GoogleOAuthProvider(
                client_id="945696136373-49as9puosd80ec9c37856fifke1qlun7.apps.googleusercontent.com",
                client_secret= "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",
                redirect_url="http://localhost:8550/api/oauth/redirect"
          )

            page.login(provider)

            def on_login(e):
                 print(page.auth.user)
                 page.go("/")
            
            page.on_login = on_login
             



        return ft.View(
            "/register",
            controls=[ 

                Container(
                        alignment=alignment.center,
                        content=Text(
                            "Regístrate",
                            size=30,
                            text_align="center",
                            weight="bold",
                            color="black",

                        ),
                ),


                
                
                Column(
                    horizontal_alignment="center",
                    controls=[
                        Container(padding=1),

                        Column(
                            spacing=12,
                            controls=[
                                emailseccion,
                                contraseccion,
                            ]
                                ),
                            ]
                        ),  
                                        

                    Container(padding=5),

                     Row(
                        controls=[

                             
                            ElevatedButton(
                                text="Registrarse",
                                width=200,
                                icon=icons.APP_REGISTRATION_ROUNDED,
                                on_click= lambda _: _register_user(emailseccion.value,contraseccion.value),#aqui va la funcion de registrar usuario
                                style= ButtonStyle(

                                    color={"": ft.colors.WHITE},

                                   bgcolor = {"": ft.colors.BLACK},

                                    shape={ "": RoundedRectangleBorder(radius=6), }



                                    )
                               ),


                            ElevatedButton(
                                text="¿Ya tienes cuenta?\nInicia sesión",
                                width=200,
                                 icon=icons.LOGIN_OUTLINED, on_click=lambda _: page.go("/login"),

                                 style= ButtonStyle(

                                    color={"": ft.colors.WHITE},

                                    bgcolor = {"": ft.colors.BLACK},

                                    shape={ "": RoundedRectangleBorder(radius=6), }
                                 )
                               ),
                            ],
                        alignment="center",
                        spacing=50,
                        ),



                    Container(padding=5),

                    Column(
                        horizontal_alignment="center",
                        controls=[
                            Container(
                                content=Text("Continúa con:", size=12, color="black", text_align="center", weight="bold")
                            ),
                            self.SignInOptions("../assets/facebook.png", "Facebook"),
                            self.SignInOptions("../assets/google.png", "Google", login_google),
                            self.SignInOptions("../assets/microsoft.png", "Microsoft"),


                        ]

                    ),


                    Container(padding=5),


                                       

            ],

            vertical_alignment =  MainAxisAlignment.CENTER, 
            horizontal_alignment = CrossAxisAlignment.CENTER, 
          
        )
