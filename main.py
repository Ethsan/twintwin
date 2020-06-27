from time import time
from tkinter import *
from tkinter import font
import math
from PIL import Image, ImageTk

## les parenthese indiquent des fonctionnalites qui ne sont pas/encore implementee ou qui peuvent disparaitre si trop de probleme ##
## DISCLAIMER : si vous utilisez le systeme de file de l'objet est uniquement reserve au fonction d'animation je ne suis en aucun cas responsable de comportement innatendue ##

def noop(*arg, **kwarg):
    print('noop!')
    return 'noop'
class View(Tk):

    def __init__(self, size = (1280, 720), fps = 60, showGraph = False):                    # se lance a la creation de l'objet
        Tk.__init__(self)                               # initialisiation de la fenetre
        self.size = size                                # ( resolution personnalise pas implemente)
        self.timeout = int(1000//fps)                              # ( fps max personnalise pas implemente)
        self.geometry(('{}x{}').format(self.size[0],self.size[1]))
        self.resizable(width = False, height = False)   # pas envie de faire la fenetre de facon responsive ducoup y'a plus de problemes
        self.queue = {}                 # [id : (call, arg, kwarg)}
        self.queueId = 0                # variable incrementable pour l'attribution des ids des actions
        self.routine = {}               # {id : ((call, time, arg, kwarg), [memory, lastcall]}
        ## memory et lastcall sont stockés dans des listes meme pourqu'elle puisse etre modifiable sans modifie le dicto ##

        self.routineId = 0              # variable incrementable pour l'attribution des ids des routines
        self.after_id = 0               # id de l'update pour pouvoir l'arreter
        self.clickable = {}             # {id : (callback, arg, kwarg)}
        self.cache = set()              # liste sauvergadant des reference sans besoin d'organisation
        self.lastFrame = time()

        ## Fonctionnalite analyse perf ##
        self.showGraph = showGraph
        if showGraph:
            self.fps = [0,0]

    def mainloop(self):                         # nouveau mainloop prenant en charge la queue et les routines
        self.update()                           # lancement de update()
        Tk.mainloop(self)                       # lancement de mainloop() normale

    def clear(self, widget = None):             # permet de clean tout les elements d'un element particulier ou de la fenetre si rien n'est precise
        for each in widget.winfochildren():
            each.destroy()
        self.clean_cache()

    def clean_cache(self):                      # libere des reference a des objets pour qu'ils soient garbage collected
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
            self.routine.clear()

    def update(self): # mise a jour des animations les actions en file sont prioritaires sur les routines
        if self.inqueue():
            for id, call in self.queue.items():
                call[0](call[1], call[2])
            self.queue.clear()

        if self.isRoutine():                                                # verifie si il y a des routines
            for id, call in self.routine.items():                           # pour chaque routine je recupere son id et ses parametres
                if call[1][1] == None:                                      # verifie si c'est la premiere fois qu'elle est appele en regardant sa memoire
                    memory = call[0][0](None, 1, *call[0][2], **call[0][3]) # appel la fonction en lui donnant ce qu'elle a save / le nbr de frame d'animation ecoule et les arguments
                    if memory == True and type(memory) == type(True):       # la routine est detruite si elle renvoie True
                        self.enqueue(self.delRoutine, id)                   # je met la destruction de la routine dans la file pour ne pas soulever d'erreur au niveau du for car je modifie le dico
                    else:
                        call[1][0] = memory                                 # enregistrement donnees et je fait attention de modifie la liste et non le dico pour eviter de soulever une erreur au niveau du for
                        call[1][1] = time()

                elif time() - call[1][1] >= call[0][1]:                     # vérifie si il y a besoin d'appeler la fonction pour eviter de l'appeler et qu'elle ne charge aucune frame
                    memory = call[0][0](call[1][0], int((time() - call[1][1])/call[0][1]), *call[0][2], **call[0][3])
                    if memory == True and type(memory) == type(True):       # la routine est detruite si elle renvoie True
                        self.enqueue(self.delRoutine, id)
                    else:
                        call[1][0] = memory         #enregistrement donnees
                        call[1][1] = time()
        if self.showGraph and not time() - self.lastFrame == 0:
            ## je ne peut pas predire l'avenir donc je n'affiche pas les fps de la frame mais ca precedente pour pouvoir la comparer ##
            fps = (int(1.0/ (time() - self.lastFrame)))
            if self.fps[0] == self.fps[1] and self.fps[1] == fps:   # les trois fps sont égaux
                shape = '|'
                tiret = (0, 0)
            elif self.fps[1] < self.fps[0] and self.fps[1] < fps:   # creux de fps
                shape = '<'
                tiret = (0, self.fps[0] - self.fps[1] - 1 if self.fps[0] - self.fps[1] else 0)
            elif self.fps[1] > self.fps[0] and self.fps[1] > fps:   # pique de fps
                shape = '>'
                tiret = (self.fps[1] - self.fps[0] - 1 if self.fps[1] - self.fps[0] else 0, 0)
            elif self.fps[0] < self.fps[1] or self.fps[1] < fps:    # montee de fps
                shape = '\\'
                tiret = (self.fps[1] - self.fps[0] - 1 if self.fps[1] - self.fps[0] else 0, 0)
            elif self.fps[0] > self.fps[1] or self.fps[1] > fps:    # descente de fps
                shape = '/'
                tiret = (0, self.fps[0] - self.fps[1] - 1 if self.fps[0] - self.fps[1] else 0)
            else:                                                   # au cas ou
                shape = '|'
                tiret = (0, 0)

            nbrFps = str(self.fps[1]) if self.fps[1] // 10 else ('0' + str(self.fps[1])) # calcul du nombre de fps en calculant l'inverse du temp ecoule entre les frames et completation des dizaines par un "0" au beosin

            print(nbrFps + ' ' * abs(self.fps[1] - 1 - tiret[0]) + '¯' * tiret[0]  + shape + '¯' * tiret[1]) # affiche les fps puis le nombre d'espace necessaire et affiche des tirets pour relier les points

            self.fps = [self.fps[1], fps] # decalage de la derniere a l'avant derniere et sauvegarde de la frame en cours

        after_id = self.after(self.timeout - int(time() - self.lastFrame)*1000, self.update)
        self.lastFrame = time()
    def update_stop(self):
            self.after_cancel(self.after_id)

    def chargement(self, file, resize = None, axe = None, cache = False):   # charge une image et la redimensionne, conserve le ratio si un axe est donne
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
        img = ImageTk.PhotoImage(img)
        if cache:
            self.cache.add(img)                                             # sauvegarde de la reference a l'image pour eviter qu'elle soit garbage collected a la disparition de la reference
        return img

    def customMenu(self, canva, text, font, margin = 1, offsetX = 0, offsetY = 0, direction = 'top'):
        ## je retourne une liste des ids des boutons pour pouvoir leur attribuer des callback ##
        if direction.lower() == 'top':
            return [canva.create_text(offsetX, offsetY + margin* (i+1) + abs(font.cget('size')) * i, anchor = N,    # ancre au N et marge sur l'axe y
                                      font = font,  fill='#FFFFFF', activefill = '#A9A9A9', text = name) for i,name in enumerate(text)]
        elif direction.lower() == 'right':
            return [canva.create_text(offsetX + margin* (i+1) + abs(font.cget('size')) * i, offsetY, anchor = E,    # ancre a l'E et marge sur l'axe x
                                      font = font,  fill='#FFFFFF', activefill = '#A9A9A9', text = name) for i,name in enumerate(text)]
        elif direction.lower() == 'bot':
            return [canva.create_text(offsetX, offsetY + margin* (i+1) + abs(font.cget('size')) * i, anchor = S,    # ancre a l'S et marge sur l'axe Y
                                      font = font,  fill='#FFFFFF', activefill = '#A9A9A9', text = name) for i,name in enumerate(text)]
        elif direction.lower() == 'left':
            return [canva.create_text(offsetX + margin* (i+1) + abs(font.cget('size')) * i, offsetY, anchor = WE,   # ancre a l'WE et marge sur l'axe x
                                      font = font,  fill='#FFFFFF', activefill = '#A9A9A9', text = name) for i,name in enumerate(text)]
    def click(self, event, canva):
        x = event.x
        y = event.y
        found = canva.find_overlapping(x,y,x,y)
        if len(self.clickable):
            try:
                call = self.clickable[found[-1]]
                if callable(call):
                    call()
                elif isinstance(call, (list, tuple)):
                    if len(call) == 3:
                        call[0](*call[1], **call[2])
                    elif len(call) == 2:
                        call[0](*call[1])
                    elif len(call) == 1:
                        call[0]()
                    else:
                        raise NotImplementedError
                else:
                    raise NotImplementedError
            except KeyError:
                print('aie')
    def menu(self):
        def animation(memory, frame, scrollMax, widget, img): # animation du fond d'ecran. c'est une image répété en deux qui défile arrivé a la moitié remonte et donne l'illusion d'une image défilant à l'infinie
            if memory == None:
                memory = 0
            if memory + frame < scrollMax:
                widget.move(img, 0, - frame) # defilement
                return memory + frame
            else:
                widget.move(img, 0, memory - frame) # replacement
                return 0

        def play(self, canva, clickable, font, margin, offset):
            if len(clickable):
                for each in clickable:
                    canva.delete(each)
                clickable.clear()
            MENU = (("Join", "Host", "Back"), ((print, ("Join", )), (print, ("Host", )), (title, (self, canva, clickable, TITLE, MARGIN, (self.size[0]//2, imageLogo.height()))))) # (a,) correspond a tuple(a)
            button = self.customMenu(canva, MENU[0], font, margin, offset[0], offset[1], direction = 'top')
            for i,each in enumerate(button):
                    clickable[each] = MENU[1][i]

        def title(self, canva, clickable, font, margin, offset):
            if len(clickable):
                for each in clickable:
                    canva.delete(each)
                clickable.clear()
            MENU = (("Play", "Option", "Quit"), ((play, (self, canva, clickable, TITLE, MARGIN, (self.size[0]//2, imageLogo.height()))), (print, ("Option", )), self.destroy)) # (a,) correspond a tuple(a)
            button = self.customMenu(canva, MENU[0], font, margin, offset[0], offset[1], direction = 'top')
            for i,each in enumerate(button):
                    clickable[each] = MENU[1][i]

        ## Constantes de mise en page ##
        TITLE = font.Font(root = self.master, family="Verdana", size=-36, weight=font.BOLD)
        MARGIN = 40

        ## Chargement page ##
        canva = Canvas(self, width=self.size[0], height=self.size[1])                   # création du cadre
        canva.pack()                                                                    # placement du cadre

        imageBg = self.chargement('bgtwin.png', self.size[0], 'x', cache = True)        # redimension du bg a la largeur de la fenetre
        bg = canva.create_image((0, 0), anchor = NW, image=imageBg)                     # affichage image bg

        imageLogo = self.chargement('twintwin.gif', self.size[0]//3, 'x', cache = True) # redimension du logo a un tier de la largeur de la fenetre
        logo = canva.create_image((self.size[0]//2, 0), anchor = N, image=imageLogo)

        self.newRoutine(animation, 0.01, imageBg.height()//2, canva, bg)                # creation de la routine de l'animation du fond

        ## Creation des boutons ##
        title(self, canva, self.clickable, TITLE, MARGIN, (self.size[0]//2, imageLogo.height()))
        canva.bind('<Button>', lambda evt : self.click(evt, canva))                     # je passe par une fonction lambda pour rajouter canva en argument a click

view = View(showGraph = True)   # initilisation
view.menu()                     # initilisation du menu
view.mainloop()                 # lancement du rendue
