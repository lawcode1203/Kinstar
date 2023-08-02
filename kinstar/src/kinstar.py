# Kinstar v1.6
import sys
import pygame
from pygame.locals import *
import random

colors = {"brown":(118,66,36),"red":(255,0,0),"green":(0,255,0),"blue":(0,0,255),"yellow":(255,255,0),"purple":(255,0,255),"white":(255,255,255),"black":(0,0,0)}
name_colors = {"X":"white","b":"black","c":"red","d":"green","a":"purple"}

class field:
    def generate_2D(size_x,size_y):
        out={}
        for a in range(size_x):
            for b in range(size_y):
                out.setdefault((a,b),"X")
        return out
    def generate_3D(size_x,size_y,size_z,min_y=0):
        out={}
        for a in range(size_x+1):
            for b in range(min_y,size_y+1):
                for c in range(size_z+1):
                    out.setdefault((a,b,c),"X")
        return out
    def update(f_data,coords,new):
        try:
            f_data.pop(coords)
        except:
            print("OUT OF RANGE ERROR OCCURED",file=sys.stderr)
            raise SyntaxError("OUT OF RANGE")
        f_data.setdefault(coords,new)
    def getat(f_data,coords):
        return f_data.get(coords)
    def raw_to_kinstar(diction,compressed=False): #Currently only works on 2D data
        """Changes raw dict data of the format: {(int1,int2):"STUFF"} to Kinstar field format"""
        max_x=0
        min_x=100000
        max_y=0
        min_y=100000
        for item in diction:
            if item[0] < 0:
                raise SyntaxError("FAIL, NEGATIVE X DATA IS UNACCEPTABLE")
            elif item[0] > 20000:
                raise SyntaxError("FAIL, TOO LARGE X IS UNACCEPTABLE")
            else:
                if item[0] > max_x:
                    max_x = item[0]
                if item[0] < min_x:
                    min_x = item[0]
        for item in diction:
            if item[1] < 0:
                raise SyntaxError("FAIL, NEGATIVE Y DATA IS UNACCEPTABLE")
            elif item[1] > 20000:
                raise SyntaxError("FAIL, TOO LARGE Y IS UNACCEPTABLE")
            else:
                if item[1] > max_y:
                    max_y = item[1]
                if item[1] < min_y:
                    min_y = item[1]
        if min_x != 0 or min_y != 0:
            raise SyntaxError("FAIL, MIN X OR Y NOT 0")
        else:
            fiel = field.generate_2D(max_x+1,max_y+1)
            for item in diction:
                field.update(fiel,item,diction.get(item))
            if compressed:
                return compression.compress(fiel)
            else:
                return fiel
    def field_max_sizes(field): #Returns the size that the field was generated with
        max_x = -1
        max_y= -1
        for spot in field:
            spot_x=spot[0]
            spot_y=spot[1]
            if spot_x > max_x:
                max_x = spot_x
            if spot_y > max_y:
                max_y = spot_y
        return (max_x+1,max_y+1)
    def sort(field):
        d = []
        for item in field:
            d.append(item)
        d.sort()
        out = {}
        for item in d:
            out.setdefault(item,field.get(item))
        return out

class compression: # Deals with the transformation between limited and unlimited field data.
    def compress(field_data):
        out={}
        for item in field_data:
            if field_data.get(item) == "X":
                pass
            else:
                out.setdefault(item,field_data.get(item))
        return out
    def decompress(compressed_field_data,x,y):
        outer = {}
        for i in range(x):
            for g in range(y):
                if compressed_field_data.get((i,g)) == None:
                    #print((i,g))
                    outer.setdefault((i,g),"X")
                else:
                    outer.setdefault((i,g),compressed_field_data.get((i,g)))
        return outer
    def iscompressed(field_data):
        foundx = False
        for item in field_data:
            if field_data.get(item) == "X":
                foundx = True
                break

        return not foundx
        

class graphics: #Graphics package
    import turtle
    ascii_relations={"X":"X","boosh":"MW"}
    def new_relation(name,icon): #Note, in order for the graphics to run smoothly, an icon of one character is required.
        graphics.ascii_relations.setdefault(name,icon)
    def delete_relation(name):
        graphics.ascii_relations.pop(name)
    def get_relation(name):
        return graphics.ascii_relations.get(name)
    def ascii_display(field_data): #Note! This only works with non-compressed field data.
        max_x,max_y = field.field_max_sizes(field_data)[0],field.field_max_sizes(field_data)[1]
        diction=[]
        c=0
        tx=0
        ty=max_y-1
        for item in field_data:
            diction.append((tx,ty))
            tx+=1
            if tx >= max_x:
                tx=0
                ty-=1
        to_print=""
        for item in diction:
            try:
                to_print+= graphics.get_relation(field_data.get(item))+" "
            except:
                raise SyntaxError("NO GRAPHICS RELATION FOR: " + str(field_data.get(item)))
            c+=1
            if c == max_x:
                to_print += "\n"
                c=0
        print(to_print)

class kinpygame: # Kinstar-Pygame package
    def setup():
        pygame.init()
    def makescreen(size=(600,800)):
        return pygame.display.set_mode(size, pygame.RESIZABLE)
    def getkeypress():         
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                return event.key
    def animate():
        pygame.display.update()
    def addtext(screen,text,size,pos,RGB,backgroundRGB,font="Menlo"):
        pygame.font.init()
        myFont = pygame.font.SysFont(font,size)
        firstText = myFont.render(text,True,RGB,backgroundRGB)
        firstTextRect = firstText.get_rect()
        firstTextRect.left = pos[0]
        firstTextRect.top = pos[1]
        screen.blit(firstText,firstTextRect)
        kinpygame.animate()
    def add_color(name,color):
        global name_colors
        global colors
        name_colors.setdefault(name,colors.get(color))
    def add_rgb(name,rgb):
        global name_colors
        name_colors.setdefault(name,rgb)
    def rand_test_field(x,y):
        fiel = field.generate_2D(x,y)
        fiel2 = field.generate_2D(x,y)
        for space in fiel:
            b_space = (abs(space[0]-1),abs(space[1]))
            if fiel2.get(b_space) == "a":
                field.update(fiel2,space,random.choice("ab"))
            elif fiel2.get(b_space) == "b":
                field.update(fiel2,space,random.choice("ab"))
            elif fiel2.get(b_space) == "c":
                field.update(fiel2,space,random.choice("abcd"))
            elif fiel2.get(b_space) == "d":
                field.update(fiel2,space,random.choice("abcd"))
            else:
                field.update(fiel2,space,random.choice("ab"))
        return fiel2

    def display_field(fiel,mag=1):
        global name_colors
        x,y=field.field_max_sizes(fiel)[0],field.field_max_sizes(fiel)[1]
        screen = kinpygame.makescreen(size=(x*mag,y*mag))
        screen.fill((255,255,255))
        for space in fiel:
            pygame.draw.rect(screen,name_colors.get(fiel.get(space)),pygame.rect.Rect(space[0]*mag,space[1]*mag,1*mag,1*mag))
        kinpygame.animate()

    def sort(fiel):
        d = []
        for item in fiel:
            d.append(item)

        d.sort()
        out = {}
        for item in d:
            out.setdefualt(item,fiel.get(item))
        return out

        
class sprite:
    sprite_attributes = {"test11038":("funny","red")}
    def new_sprite(field_data,name,starting_coords):
        field.update(field_data,starting_coords,name)
    def delete_sprite(field_data,coords):
        field.update(field_data,coords,"X")
    def newcoords_f(field_data,name,starting_coords,next_coords): #Forces a move
        sprite.delete_sprite(field_data,starting_coords)
        sprite.new_sprite(field_data,name,next_coords)
    def newcoords(field_data,name,starting_coords,next_coords,allowed=["X"]): # Attempts to move to an unowned space
        if field.getat(field_data,next_coords) == "X":
            sprite.newcoords_f(field_data,name,starting_coords,next_coords)
        else:
            return "FAIL"
    def getsprite(field_data,name): #WARNING! USE AT YOUR OWN RISK! ONLY WORKS WHEN ONLY ONE SPRITE WITH A PARTICULAR NAME EXISTS!
        for item in field_data:
            if field_data.get(item) == name:
                return item
        return "FAIL"
    def add_attribute(sprite, attribute_data):
        sprite_attributes.setdefault(sprite,attribute_data)
    def delete_attribute(sprite):
        sprite_attributes.pop(sprite)
    def change_attribute(sprite, attribute_data):
        delete_attribute(sprite)
        add_attribute(sprite, attribute_data)
    def get_attribute(sprite):
        x=sprite_attributes.get(sprite)
        if x != None:
            return x
        else:
            raise SyntaxError("Invalid attribute call. Sprite attributes do no exist.")
    def easymove(field_data,name,changex,changey):
       if sprite.newcoords(field_data,name,sprite.getsprite(field_data,name),(sprite.getsprite(field_data,name)[0]+changex, sprite.getsprite(field_data,name)[1]+changey)) == "FAIL":
           return "FAIL"
