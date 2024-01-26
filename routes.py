from packages.flet_route import path
from middlewares.url_middleware import UrlBasedMiddleware
from views.index_view import IndexView 
from views.menu import MenuView
from views.profile import ProfileView

app_routes = [
    path(url="/",clear=True,view=IndexView().view), 
    path(url="/menu",clear=True,view= MenuView().view), 
    path(url="/profile",clear=True,view= ProfileView().view), 
    path(url="/api/oauth/redirect", clear=True, view=IndexView().view, middleware = UrlBasedMiddleware().call_me)

]

