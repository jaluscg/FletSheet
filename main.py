from flet import *



def main(page: Page):

   

    page.add(
        SafeArea(
            content= Text("Intento de que funcione esto No1", size=30, color="black"))
            )
    


   


#app(main)

app(main, view=AppView.WEB_BROWSER)