from threading import Thread
from time import sleep
from tkinter import *
from tkinter import font
import math

from PIL import Image, ImageTk

def noop():
    pass

def chargement(file, resize = None, axe = None): # charge une image et la redimensionne, conserve le ratio si un axe est donné
    img = Image.open(file)
    if resize is not None:
        if axe is None:
            img = img.resize(resize, Image.ANTIALIAS)
        elif axe == "x":
            resize = (resize, resize * img.size[1] // img.size[0])
            img = img.resize(resize, Image.ANTIALIAS)
        elif axe == "y":
            resize = (resize * img.size[0] // img.size[1], resize)
            img = img.resize(resize, Image.ANTIALIAS)
    return ImageTk.PhotoImage(img)

class View(Tk):

    def __init__(self, size = None): # se lance à la creation de l'objet
        Tk.__init__(self) # initialisiation fenetre
        self.size = size or (1280, 720) # implementation futur ou proche de résolution personnalisée
        self.geometry(('{}x{}').format(self.size[0],self.size[1]))
        self.resizable(width = False, height = False) # pas envie de faire la fenetre de facon responsive ducoup y a plus de problème
        self.protocol("WM_DELETE_WINDOW", self.close) # la croix appel close()
        self.thread = []
        Thread(target=self.menu).start() # démarrage en parallèle du menu pour ne pas bloquer le flux

    def close(self):
        self.destroy() # ferme la fenetre

    def menu(self):

        def animation(): # animation du fond d'ecran. c'est une image répété en deux qui défile arrivé a la moitié remonte et donne l'illusion d'une image défilant à l'infinie
            scrollMax = imageBg.height()//2 
            position = 0
            try:
                while True: # vérifie si l'animation doit s'arrêter ou si l'application doit s'arrêter/ en faite nique la stabilité
                    if position < scrollMax:
                        position += 1
                        canva.move(bg, 0, -1) # defilement
                        sleep(0.01)
                    else:
                        canva.move(bg, 0, scrollMax) # replacement
                        position = 0
            except TclError: # j'attrape les erreurs meme si elle remonte pas dans le main thread parceque c'est moche des messages rouges
                print('aïe')

        def click(event, widget, button):
            x = event.x
            y = event.y
            found = widget.find_overlapping(x,y,x,y)
            if len(found) > 1:
                try:
                    index = button[0].index(found[-1])
                    button[1][index]()
                except ValueError:
                    print('aie')
                    # envie de mourir y avait deja une methode pour faire quelque chose de similaire

        
        # les fonctions pour les boutons ( pour l'instant elle ne font rien de particulier)
        def createButton(text):
            return [canva.create_text(self.size[0]//2, offset + MARGIN * (i+1) + abs(TITLE.cget('size')) * i, anchor = N,
                                                fill='#FFFFFF', activefill = '#A9A9A9', text = name, font = TITLE) for i,name in enumerate(text)]
        
        def menu():
            def play():
                def host():
                    print('host')
                def join():
                    print('join')
                PLAY = ['Host', 'Join', 'Back']
                for each in self.button[0]:
                    canva.delete(each)
                temp = createButton(PLAY)
                self.button = (temp, (host, join, menu))
            def option():
                print('option')
            MENU = ['Play', 'Option', 'Quit']
            if self.button:
                for each in self.button[0]:
                    canva.delete(each)
            temp = createButton(MENU)
            self.button = (temp, (play, option , self.close))
        #déclaration de mes constantes
                    
        TITLE = font.Font(family="Verdana", size=-36, weight=font.BOLD)
        MARGIN = 40
                     # liste des focntions lié aux items
        
        canva = Canvas(self, width=self.size[0], height=self.size[1]) # création du cadre
        canva.pack()

        imageBg = chargement('bgtwin.png', self.size[0], 'x') # redimension du bg a la largeur de la fenetre
        bg = canva.create_image((0, 0), anchor = NW, image=imageBg) # affichage image bg

        Thread(target = animation).start() # lancement en paralléle de l'animation

        imageLogo = chargement('twintwin.gif', self.size[0]//3, 'x') # redimension du logo a un tier de la largeur de la fenetre
        logo = canva.create_image((self.size[0]//2, 0), anchor = N, image=imageLogo) # affichage logo

        # création des boutons à partir de la liste des items
        offset = imageLogo.height()
        self.button = []
        menu() # i correspondrait a "i in range(len(MENU))" et name a "name in MENU"
        canva.bind('<Button>', lambda event:click(event, canva, self.button)) # appel click si clique sur la fenetre
        
    def play(self):
        def delete(evt):
            del play
            print(play)
        play = Canvas(self, width=self.size[0], height=self.size[1]) # création du cadre
        play.pack()
        play.imageBg = chargement('bgtwin.png', self.size[0], 'x') # redimension du bg a la largeur de la fenetre
        bg = play.create_image((0, 0), anchor = NW, image=play.imageBg)
        play.bind('<Button>', delete)

View().mainloop()
