from threading import Thread
from time import sleep
from tkinter import *
from tkinter import font
import math

from PIL import Image, ImageTk

def noop():
    pass

def chargement(file, resize = None, axe = None):
    img = Image.open(file)
    if resize is not None:
        if axe is None:
            img = img.resize(resize, Image.ANTIALIAS)
        elif axe == "x":
            resize = (resize, resize * img.size[1] // img.size[0])
            img = img.resize(resize, Image.NEAREST)
        elif axe == "y":
            resize = (resize * img.size[0] // img.size[1], resize)
            img = img.resize(resize, Image.ANTIALIAS)
    return ImageTk.PhotoImage(img)

class View(Tk):

    def __init__(self, size = None):
        Tk.__init__(self)
        self.running = True
        self.size = size or (1280, 720) # implementation futur ou proche de résolution personnalisée
        self.geometry(('{}x{}').format(self.size[0],self.size[1]))
        self.resizable(width = False, height = False) # pas envie de faire la fenetre de facon responsive ducoup y a plus de problème
        self.protocol("WM_DELETE_WINDOW", self.close) # la croix appel close()
        Thread(target=self.menu).start() # démarrage en parallèle du menu pour ne pas bloquer le flux

    def close(self):
        self.running = False
        sleep(0.2) # attendre que tous les threads se terminent
        self.destroy()

    def menu(self):

        def animation():
            self.menu_active = True
            scrollMax = imageBg.height()//2
            position = 0
            while self.menu_active and self.running:
                if position < scrollMax:
                    position += 1
                    menu.move(bg, 0, -1)
                    sleep(0.01)
                else:
                    menu.move(bg, 0, scrollMax)
                    position = 0

        def click(event):
            x = event.x
            y = event.y
            size = abs(MENU_TITLE.cget('size'))
            offset = imageLogo.height()
            if y > offset + MENU_MARGIN and y < offset + MENU_MARGIN * len(MENU) + size * len(MENU):
                for i in range(len(MENU)):
                    if y > offset + MENU_MARGIN * (i + 1) + size * i and y < offset + MENU_MARGIN * (i + 1) + size * (i + 1):
                        MENU_CALLBACK[i]()

        def play():
            print('play')

        def option():
            print('option')

        def leave():
            self.close()

        def stop():
            self.menu_active = False
            print("stop")

        MENU_TITLE = font.Font(family="Verdana", size=-36, weight=font.BOLD)
        MENU_MARGIN = 40
        MENU = ['Play', 'Option', 'Quit']
        MENU_CALLBACK = [play, option , leave]


        menu = Canvas(self, width=self.size[0], height=self.size[1])
        menu.pack()

        imageBg = chargement('bgtwin.jpg', self.size[0], 'x')
        bg = menu.create_image((0, 0), anchor = NW, image=imageBg)

        Thread(target = animation, args = ()).start()

        imageLogo = chargement('twintwin.gif', self.size[0]//3, 'x')
        logo = menu.create_image((self.size[0]//2, 0), anchor = N, image=imageLogo)

        button = [menu.create_text(self.size[0]//2, imageLogo.height() + MENU_MARGIN * (i+1) + abs(MENU_TITLE.cget('size')) * i, anchor = N,
                                                fill='#FFFFFF', activefill = '#A9A9A9', text = name, font = MENU_TITLE) for i,name in enumerate(MENU)]
        menu.bind('<Button>', click)

view = View()
view.mainloop()
