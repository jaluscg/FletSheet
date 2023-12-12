from PIL import Image

filename = "icon.png"
img = Image.open(filename)
img.save("icon.ico", format='ICO', sizes=[(32, 32)])
