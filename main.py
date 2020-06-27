from time import time
from tkinter import *
from tkinter import font
import math
from PIL import Image, ImageTk

## les parenthese indiquent des fonctionnalites qui ne sont pas/encore implementee ou qui peuvent disparaitre si trop de probleme ##
## DISCLAIMER : si vous utilisez le systeme de file de l'objet est uniquement reserve au fonction d'animation je ne suis en aucun cas responsable de comportement innatendue ##

def chargement(file, resize = None, axe = None):    # charge une image et la redimensionne, conserve le ratio si un axe est donne
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

    def __init__(self, size = (1280, 720), fps = 60):                    # se lance a la creation de l'objet
        Tk.__init__(self)                               # initialisiation de la fenetre
        self.size = size                                # ( resolution personnalise pas implemente)
        self.timeout = int(1000//fps)                              # ( fpsmax personnalise pas implemente)
        self.geometry(('{}x{}').format(self.size[0],self.size[1]))
        self.resizable(width = False, height = False)   # pas envie de faire la fenetre de facon responsive ducoup y'a plus de problemes
        self.queue = {}                 # [id : (call, arg, kwarg)}
        self.queueId = 0                # variable incrementable pour l'attribution des ids des actions
        self.routine = {}               # {id : ((call, time, arg, kwarg), [memory, lastcall]}
    ## memory et lastcall sont stockés dans des listes meme pourqu'elle puisse etre modifiable sans modifie le dicto ##
        self.routineId = 0              # variable incrementable pour l'attribution des ids des routines
        self.after_id = 0               # id de l'update pour pouvoir l'arreter
        self.cache = set()              # liste sauvergadant des reference sans besoin d'organisation

    def mainloop(self):                         # nouveau mainloop prenant en charge la queue et les routines
        self.update()
        Tk.mainloop(self)

    def clear(self, widget = None):             # permet de clean tout les elements d'un element particulier ou de la fenetre si rien n'est precise
        for each in widget.winfochildren():
            each.destroy()
        self.clean_cache()

    def clean_cache(self):
        self.cache.clear()

    def enqueue(self, call, *arg, **kwarg):     # mise en file d'attente d'une action et de ses arguments
        self.queueId += 1
        self.queue[self.queueId] = (call, arg, kwarg)
        return self.queueId                     # return l'id de l'action

    def inqueue(self, id = None):               # permet de savoir si une action se trouve dans la file ou de savoir si il reste des actions si aucune action n'est precise
        if not id == None:
            try:
                return self.queue[id]
            except KeyError:
                return False
        else:
            if len(self.queue):
                return True
            else:
                return False

    def delqueue(self, id = None):              # permet de supprimer une action de la file ou de vider la file si aucune action n'est precise
        if not id == None:
            try:
                del self.queue[id]
            except KeyError:
                return False
        else:
            self.queue.clear()

    def newRoutine(self, call, time, *arg, **kwarg): # permet de creer une nouvelle routine ( time en testa voir si viable )
        self.routineId += 1
        self.routine[self.routineId] = ((call, time, arg, kwarg), [None, None])
        return self.routineId                   # return l'id de la routine

    def isRoutine(self, id = None):             # agi de la meme facon que pour la file (cf. l.50)
        if not id == None:
            try:
                return self.routine[id]
            except KeyError:
                return False
        else:
            if len(self.routine):
                return True
            else:
                return False

    def delRoutine(self, id = None):            # agi de la meme facon que pour la file (cf. l.62)
        if not id == None:
            try:
                del self.routine[id]
            except KeyError:
                return False
        else:
            self.routine.clear() # ( implementation time )

    def update(self): # mise a jour des animations les actions en file sont prioritaires sur les routines
        if self.inqueue():
            for id, call in self.queue.items():
                call[0](call[1], call[2])
            self.queue.clear()
##        if self.isRoutine():
##            for index,call in enumerate(self.routine[1]):
##                memory = call[0](self.routine[2][index], *call[2], **call[3])
##                if memory == True and type(memory) == type(True): # la routine est detruite si elle renvoie True
##                    self.delRoutine(self.routine[0][index])
##                else:
##                    self.routine[2][index] = memory

        if self.isRoutine():   # ( implementation time )
            for id, call in self.routine.items():
                print(call)
                if call[1][1] == None:
                    memory = call[0][0](None, 1, *call[0][2], **call[0][3]) # appel la fonction en lui donnant ce qu'elle a save / le nbr de frame d'animation passe et les arguments
                    if memory == True and type(memory) == type(True):          # la routine est detruite si elle renvoie True
                        self.enqueue(self.delRoutine, id)
                    else:
                        call[1][0] = memory         #enregistrement donnees
                        call[1][1] = time()
                        
                elif time() - call[1][1] >= call[0][1]:
                    memory = call[0][0](call[1][0], int((time() - call[1][1])/call[0][1]), *call[0][2], **call[0][3])
                    if memory == True and type(memory) == type(True):          # la routine est detruite si elle renvoie True
                        self.enqueue(self.delRoutine, id)       # mise en file sinon changement taille pendant iteration 
                    else:
                        call[1][0] = memory         #enregistrement donnees
                        call[1][1] = time()

        after_id = self.after(self.timeout, self.update)

    def update_stop(self):
        self.after_cancel(self.after_id)

    def menu(self):
        def animation(memory, frame, scrollMax, widget, img): # animation du fond d'ecran. c'est une image répété en deux qui défile arrivé a la moitié remonte et donne l'illusion d'une image défilant à l'infinie
            if memory == None:
                memory = 0
            if memory + frame < scrollMax:
                widget.move(img, 0, -frame) # defilement
                return memory + frame
            else:
                widget.move(img, 0, memory) # replacement
                return 0
        ## Constantes de mise en page ##
        TITLE = font.Font(root = self.master, family="Verdana", size=-36, weight=font.BOLD)
        MARGIN = 40
        ## Chargement page ##
        canva = Canvas(self, width=self.size[0], height=self.size[1])                   # création du cadre
        canva.pack()                                                                    # affichage du cadre
        imageBg = chargement('bgtwin.png', self.size[0], 'x')                           # redimension du bg a la largeur de la fenetre
        bg = canva.create_image((0, 0), anchor = NW, image=imageBg)                     # affichage image bg
        self.cache.add(imageBg)                                                         # sauvergarde de la reference a l'image pour eviter d'etre garbage collected
        imageLogo = chargement('twintwin.gif', self.size[0]//3, 'x')                    # redimension du logo a un tier de la largeur de la fenetre
        logo = canva.create_image((self.size[0]//2, 0), anchor = N, image=imageLogo)
        self.cache.add(imageLogo)

        self.newRoutine(animation, 0.01, imageBg.height()//2, canva, bg)                # creation de la routine de l'animation du fond
        ## Creation des boutons ##
        offset = imageLogo.height()
        canva.bind('<Button>', lambda evt:print('click'))

test = View()
test.menu()
test.mainloop()
