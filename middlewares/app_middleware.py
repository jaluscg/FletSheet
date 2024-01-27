import flet as ft

class AppBasedMiddleware:
    def __init__(self):
        ...

    def call_me(self,page:ft.Page):

        print("App Based Middleware Called")
        #page.route = "/another_view" # If you want to change the route for some reason, use page.route
