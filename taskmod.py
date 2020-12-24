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

async def prep_books(screen, actualwidth, actualheight):
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