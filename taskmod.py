import asyncio
import colorsys
import json
import sys
import math
import os
import pygame as pg
from pygame.locals import *
import time
import websockets
import traceback
import random

import numpy as np

functions = [None]*256
prep = [None]*256
inputs = [None]*256

prep[128] = "prep_books"
functions[128] = "display_books"
inputs[128] = "return_books"

prep[200] = "prep_line"
functions[200] = "display_line"
inputs[200] = "wait_line"

taskdesc = [""]*256
taskdesc[128] = "Koerner: Return library books"
taskdesc[200] = "Sauder: Wait in line for food"

bookbase = pg.image.load("sprites/book.png").convert_alpha()

def taskbase(actualwidth, actualheight):
  prime = pg.Surface((actualwidth, actualheight), pg.SRCALPHA)
  surf = pg.Surface((actualwidth//2, actualwidth//2), pg.SRCALPHA)
  surf.fill((128, 128, 128, 128))
  prime.blit(surf, (actualwidth//4, actualheight//2 - actualwidth//4))
  return prime

def fill(surface, color):
  # https://stackoverflow.com/questions/42821442/how-do-i-change-the-colour-of-an-image-in-pygame-without-changing-its-transparen
  surface = surface.copy()
  w, h = surface.get_size()
  r, g, b = color
  for x in range(w):
    for y in range(h):
      col = surface.get_at((x, y))
      if col[2] == 61:
        surface.set_at((x, y), pg.Color(r, g, b, 255))
  return surface


"""

LIBRARY BOOKS

"""

async def prep_books(screen, actualwidth, actualheight, player):
  books = []
  rbooks = []
  bookoffsets = []
  for i in np.linspace(actualwidth//4, actualwidth//2, 5):
    col = [random.randint(0, 255) for whoevencares in range(3)]
    book = pg.transform.flip(pg.transform.rotozoom(fill(bookbase, col), random.randrange(0, 360), random.randrange(50, 125)/100), random.getrandbits(1), random.getrandbits(1))
    b = book.copy()
    rbooks.append(book)
    b.fill((0,0,0), special_flags=pg.BLEND_RGB_MULT)
    surf = pg.Surface((actualwidth, actualheight))
    surf.fill((255, 255, 255))
    surf.blit(b, (i, actualheight//2))
    bookoffsets.append([i, actualheight//2])
    books.append(surf)

  land_collider =  pg.Surface((actualwidth, actualheight))
  land_collider.fill((255, 255, 255))
  land_collider.blit(pg.transform.scale(pg.image.load("colliders/bookdrop.png"), (383*2, 383*2)), (actualwidth//4 + 1, actualheight//2 - (actualwidth//4 - 1)))
  
  return books, rbooks, bookoffsets, land_collider

async def display_books(entries, screen, actualwidth, actualheight):
  screen.blit(pg.transform.scale(pg.image.load("sprites/bookdrop.png").convert_alpha(), (383*2, 383*2)), (actualwidth//4 + 1, actualheight//2 - (actualwidth//4 - 1)))
  books, rbooks, bookoffsets, _ = entries
  for i in range(len(books)):
    screen.blit(rbooks[i], bookoffsets[i])

async def return_books(entries, screen, actualwidth, actualheight, dmx, dmy, is_hover, clicked):
  finished = False
  books, rbooks, bookoffsets, land_collider = entries
  mpx, mpy = pg.mouse.get_pos()
  update_render = False

  if is_hover != -1 and any(pg.mouse.get_pressed()):
    clicked = True
    if dmx != mpx or dmy != mpy:
      bookoffsets[is_hover][0] -= dmx-mpx
      bookoffsets[is_hover][1] -= dmy-mpy
      bruh = rbooks[is_hover].copy()
      bruh.fill((0,0,0), special_flags=pg.BLEND_RGB_MULT)
      surf = pg.Surface((actualwidth, actualheight))
      surf.fill((255, 255, 255))
      surf.blit(bruh, bookoffsets[is_hover])
      books[is_hover] = surf
      update_render = True

  elif not any(pg.mouse.get_pressed()):
    clicked = False
    if is_hover != -1 and land_collider.get_at((mpx, mpy))[0] != 255:
      del books[is_hover]
      del rbooks[is_hover]
      del bookoffsets[is_hover]
      is_hover = -1
      pg.mouse.set_cursor(*pg.cursors.arrow)
      update_render = True
      if len(books) == 0: finished = True

  intersecting = False
  for b in range(len(books)-1, -1, -1):
    if books[b].get_at((mpx, mpy))[0] == 0:
      intersecting = True
      if not clicked:
        is_hover = b
        pg.mouse.set_cursor(*pg.cursors.diamond)
      break

  if not intersecting:
    if is_hover != -1:
      is_hover = -1
      pg.mouse.set_cursor(*pg.cursors.arrow)

  return is_hover, clicked, mpx, mpy, update_render, finished

"""

PARKING TICKET

"""

async def prep_ticket(screen, actualwidth, actualheight, player):
  books = []
  rbooks = []
  bookoffsets = []
  
  
  return books, rbooks, bookoffsets, land_collider

async def display_ticket(entries, screen, actualwidth, actualheight):
  screen.blit(pg.transform.scale(pg.image.load("sprites/bookdrop.png").convert_alpha(), (383*2, 383*2)), (actualwidth//4 + 1, actualheight//2 - (actualwidth//4 - 1)))
  books, rbooks, bookoffsets, _ = entries
  for i in range(len(books)):
    screen.blit(rbooks[i], bookoffsets[i])

async def pay_ticket(entries, screen, actualwidth, actualheight, dmx, dmy, is_hover, clicked):
  finished = False
  books, rbooks, bookoffsets, land_collider = entries
  mpx, mpy = pg.mouse.get_pos()
  update_render = False

  if is_hover != -1 and any(pg.mouse.get_pressed()):
    clicked = True
    if dmx != mpx or dmy != mpy:
      bookoffsets[is_hover][0] -= dmx-mpx
      bookoffsets[is_hover][1] -= dmy-mpy
      bruh = rbooks[is_hover].copy()
      bruh.fill((0,0,0), special_flags=pg.BLEND_RGB_MULT)
      surf = pg.Surface((actualwidth, actualheight))
      surf.fill((255, 255, 255))
      surf.blit(bruh, bookoffsets[is_hover])
      books[is_hover] = surf
      update_render = True

  elif not any(pg.mouse.get_pressed()):
    clicked = False
    if is_hover != -1 and land_collider.get_at((mpx, mpy))[0] != 255:
      del books[is_hover]
      del rbooks[is_hover]
      del bookoffsets[is_hover]
      is_hover = -1
      pg.mouse.set_cursor(*pg.cursors.arrow)
      update_render = True
      if len(books) == 0: finished = True

  intersecting = False
  for b in range(len(books)-1, -1, -1):
    if books[b].get_at((mpx, mpy))[0] == 0:
      intersecting = True
      if not clicked:
        is_hover = b
        pg.mouse.set_cursor(*pg.cursors.diamond)
      break

  if not intersecting:
    if is_hover != -1:
      is_hover = -1
      pg.mouse.set_cursor(*pg.cursors.arrow)

  return is_hover, clicked, mpx, mpy, update_render, finished

"""

WAITING IN LINE

"""

async def prep_line(screen, actualwidth, actualheight, player):
  personqueue = []
  for i in range(10):
    types = []
    col = [random.randint(0, 255) for k in range(3)]
    for filename in ["player.png", "playerwalkingfront.png", "player.png", "playerwalkingback.png"]:
      pl = pg.transform.scale(pg.image.load(filename).convert_alpha(), (66, 100))
      pl.fill(col, special_flags=pg.BLEND_RGB_MULT)
      types.append(pl)
    personqueue.append(types)

  col = [player["h"], player["s"], player["l"]]
  outputs = colorsys.hls_to_rgb(col[0]/360, col[2]/100, col[1]/100)
  types = []
  for filename in ["player.png", "playerwalkingfront.png", "player.png", "playerwalkingback.png"]:
    pl = pg.transform.scale(pg.image.load(filename).convert_alpha(), (66, 100))
    pl.fill((outputs[0]*255, outputs[1]*255, outputs[2]*255), special_flags=pg.BLEND_RGB_MULT)
    types.append(pl)
  personqueue.insert(0, types)
  cashier = pg.transform.flip(personqueue.pop(10)[0], True, False)
  return personqueue, cashier, [0, 9, 9]

async def display_line(entries, screen, actualwidth, actualheight):
  personqueue, cashier, renderstate = entries
  for i in range(len(personqueue)):
    if personqueue[i]:
      if i == renderstate[1]: 
        pos = actualwidth//4 + i * 66 + renderstate[0]
        which = personqueue[i][renderstate[0]//3]
      else: 
        pos = actualwidth//4 + i * 66
        which = personqueue[i][0]
      screen.blit(which, (pos, actualheight//2))
  screen.blit(cashier, (actualwidth//4 + (i+2) * 66 - 30, actualheight//2))
  pg.draw.rect(screen, (128, 128, 128), pg.Rect(actualwidth//4 + (i+1)*66 + 10, actualheight//2 + 50, 33, 50))

async def wait_line(entries, screen, actualwidth, actualheight, dmx, dmy, is_hover, clicked):
  finished = False
  personqueue, cashier, renderstate = entries
  mpx, mpy = pg.mouse.get_pos()
  update_render = False

  if renderstate[1] != 0:
    update_render = True
    renderstate[0] += 1

  if renderstate[0] == 9:
    renderstate[0] = 0
    renderstate[1] -= 1
    personqueue.pop(renderstate[1]+1)
    personqueue.insert(renderstate[1], None)

  if renderstate[1] == 0:
    renderstate[1] = 9
    renderstate[2] -= 1
    if not any(personqueue[9:]):
      finished = True

  return is_hover, clicked, mpx, mpy, update_render, finished
