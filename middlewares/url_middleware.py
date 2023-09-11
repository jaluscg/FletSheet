import flet as ft
from flet_route import Params,Basket

class UrlBasedMiddleware:
    def __init__(self):
        ...

    def call_me(self,page:ft.Page,params:Params,basket:Basket):

        print("Url Based Middleware Called")
        #page.route = "/another_view" # If you want to change the route for some reason, use page.route
