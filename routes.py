from flet_route import path
from views.index_view import IndexView 
from views.menu import MenuView

app_routes = [
    path(url="/",clear=True,view=IndexView().view), 
    path(url="/menu",clear=True,view= MenuView().view),
]

