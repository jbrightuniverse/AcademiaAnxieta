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

for i in range(128, 133):
  prep[i] = "prep_books"
  functions[i] = "display_books"
  inputs[i] = "return_books"

for i in range(200, 205):
  prep[i] = "prep_line"
  functions[i] = "display_line"
  inputs[i] = "wait_line"

for i in range(75, 80):
  prep[i] = "prep_ticket"
  functions[i] = "display_ticket"
  inputs[i] = "pay_ticket"

for i in [50, 51]:
  prep[i] = "prep_timer"
  functions[i] = "display_timer"
  inputs[i] = "ticker_timer"

for i in [52, 53]:
  prep[i] = "prep_sd"
  functions[i] = "display_sd"
  inputs[i] = "eq_sd"

for i in [54, 55]:
  prep[i] = "prep_math"
  functions[i] = "display_math"
  inputs[i] = "do_math"

for i in [56, 57]:
  prep[i] = "prep_math2"
  functions[i] = "display_math2"
  inputs[i] = "do_math2"

for i in [58, 59]:
  prep[i] = "prep_list"
  functions[i] = "display_list"
  inputs[i] = "do_list"

prep[60] = "prep_e"
functions[60] = "display_e"
inputs[60] = "paint_e"

for i in range(61, 66):
  prep[i] = "prep_birb"
  functions[i] = "display_birb"
  inputs[i] = "feed_birb"

taskdesc = [""]*256
taskdesc[50] = "Scarfe: Ticker timer lab"
taskdesc[51] = "UTP: Ticker timer lab"
taskdesc[52] = "Chemistry B: ECON 101"
taskdesc[53] = "Geography: ECON 101"
taskdesc[54] = "Math: MATH 100"
taskdesc[55] = "LSK: MATH 100"
taskdesc[56] = "Math: MATH 101"
taskdesc[57] = "LSK: MATH 101"
taskdesc[58] = "Dempster: CPSC 221"
taskdesc[59] = "MacMillan: CPSC 221"
taskdesc[60] = "Main Mall: Paint E"
taskdesc[61] = "Fountain: Feed birb"
taskdesc[62] = "UTP: Feed birb"
taskdesc[63] = "UBC Exchange: Feed birb"
taskdesc[64] = "Nest: Feed birb"
taskdesc[65] = "Rose Garden: Feed birb"
taskdesc[75] = "West Parkade: Renew parking ticket"
taskdesc[76] = "North Parkade: Renew parking ticket"
taskdesc[77] = "Fraser Parkade: Renew parking ticket"
taskdesc[78] = "Health Parkade: Renew parking ticket"
taskdesc[79] = "MacInnes Parkade: Renew parking ticket"
taskdesc[128] = "Koerner: Return library books"
taskdesc[129] = "IKB: Return library books"
taskdesc[130] = "Scarfe: Return library books"
taskdesc[131] = "Woodward: Return library books"
taskdesc[132] = "Xwi7xwa: Return library books"
taskdesc[200] = "Sauder: Wait in line for food"
taskdesc[201] = "Nest: Wait in line for food"
taskdesc[202] = "Life: Wait in line for food"
taskdesc[203] = "Central: Wait in line for food"
taskdesc[204] = "Strangway: Wait in line for food"

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
  number = ""
  expected = str(random.randint(100000, 999999))
  task = list(set([int(t) for t in player["tasks"].keys()]).intersection(range(75, 79)))[0]
  locations = {
    75: "West Parkade",
    76: "North Parkade",
    77: "Fraser Parkade",
    78: "Health Parkade",
    79: "MacInnes Parkade"
  }
  return [number, expected, locations[task], time.time()]

async def display_ticket(entries, screen, actualwidth, actualheight):
  exp = entries
  number = exp[0]
  expected = exp[1]
  box = pg.Rect(actualwidth//2 - 130, actualheight//2 -20, 260, 40)
  pg.draw.rect(screen, (128, 128, 128), box)
  pg.draw.rect(screen, (255, 255, 255), box, 2)
  pg.draw.rect(screen, (255, 255, 255), pg.Rect(actualwidth//4 + 30, actualheight//2 - actualwidth//4 + 30, 200, 200))
  screen.blit(pg.font.Font("OpenSansEmoji.ttf", 28).render("Parking Ticket", True, (0,0,0)), (actualwidth//4 + 35, actualheight//2 - actualwidth//4 + 35))
  screen.blit(pg.font.Font("OpenSansEmoji.ttf", 15).render(f"ID: {expected}", True, (0,0,0)), (actualwidth//4 + 35, actualheight//2 - actualwidth//4 + 105))
  screen.blit(pg.font.Font("OpenSansEmoji.ttf", 15).render(f"Location: {exp[2]}", True, (0,0,0)), (actualwidth//4 + 35, actualheight//2 - actualwidth//4 + 140))
  if number:
    screen.blit(pg.font.Font("OpenSansEmoji.ttf", 20).render(number, True, (0,0,255)), (actualwidth//2 - 130 + 3, actualheight//2 - 20 + 3))
  
  # draw textbox

async def pay_ticket(entries, screen, actualwidth, actualheight, dmx, dmy, is_hover, clicked):
  finished = False
  exp = entries
  mpx, mpy = pg.mouse.get_pos()
  update_render = False
  keys = pg.key.get_pressed()
  if keys[K_BACKSPACE] and time.time() - entries[3] > 0.1: 
    entries[3] = time.time()
    exp[0] = exp[0][:-1]
  elif any([keys[i] for i in list(range(48, 58)) + [K_BACKSPACE]]) and time.time() - entries[3] > 0.1 and len(exp[0]) < 7:
    entries[3] = time.time()
    for i in range(48, 58):
      if keys[i]:
        exp[0] += str(i - 48)
        if exp[0] == exp[1]:
          finished = True
        break
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

"""

TICKER TIMER

"""

async def prep_timer(screen, actualwidth, actualheight, player):
  dots = []
  return dots, [actualwidth//4 + 128, False, "", False], []

async def display_timer(entries, screen, actualwidth, actualheight):
  dots, exp, _ = entries
  screen.blit(pg.image.load("sprites/timer.png").convert_alpha(), (actualwidth//4 + 1, actualheight//2 - (actualwidth//4 - 1)))
  pg.draw.rect(screen, (255, 255, 255), pg.Rect(actualwidth//4 + 1, actualheight//2 + 35, exp[0]-(actualwidth//4 + 1), 20))
  pg.draw.rect(screen, (129, 129, 129), pg.Rect(actualwidth//4 + 81, actualheight//2 + 33, 27, 24))
  screen.blit(pg.font.Font("OpenSansEmoji.ttf", 40).render("Drag the tape to reach constant velocity", True, (255,255,255)), (actualwidth//4 + 5, 3*actualheight//4))
  if exp[2]:
    screen.blit(pg.font.Font("OpenSansEmoji.ttf", 40).render(exp[2], True, (255,0,0)), (actualwidth//4 + 25, 3*actualheight//4 + 45))
  for dotx in dots:
    dot = dotx[0]
    x = exp[0] - dot
    if x > actualwidth//4 + 81 + 27:
      pg.draw.circle(screen, (35, 95, 169), (x, actualheight//2 + 45 + dotx[1]), 3)
  
async def ticker_timer(entries, screen, actualwidth, actualheight, dmx, dmy, is_hover, clicked):
  finished = False
  dots, exp, seentimes = entries
  mpx, mpy = pg.mouse.get_pos()
  update_render = False
  edge = exp[0]

  if mpx >= edge-20 and mpx <= edge and mpy >= actualheight//2 + 35 and mpy < actualheight//2 + 55:
    if is_hover == -1:
      is_hover = 1
      pg.mouse.set_cursor(*pg.cursors.diamond)

  else:
    if is_hover == 1 and not any(pg.mouse.get_pressed()):
      is_hover = -1
      pg.mouse.set_cursor(*pg.cursors.arrow)

  if any(pg.mouse.get_pressed()) and is_hover == 1 and exp[0] + mpx - dmx <= 3*actualwidth//4:
    exp[1] = True
    if mpx > dmx:
      exp[0] += mpx - dmx
      update_render = True

  elif exp[0] == 3*actualwidth//4:
    pg.mouse.set_cursor(*pg.cursors.arrow)
    positions = []
    if len(dots) < 2:
      variance = 0
    else:
      for i in range(len(dots) - 1):
        pos = dots[i+1][0] - dots[i][0]
        positions.append(pos)
      mean = sum(positions)/len(positions)
      variance = sum([(a-mean)**2 for a in positions])/len(positions)
    if variance < 225:
      if len(dots) < 5:
        exp[2] = "Minimum 5 dots. Try again."
        dots[:] = []
        exp[0] = actualwidth//4 + 128
        exp[1] = False
        exp[3] = False
        seentimes[:] = []
        is_hover = -1
      else:
        finished = True
    else:
      exp[2] = "Not constant enough. Try again."
      dots[:] = []
      exp[0] = actualwidth//4 + 128
      exp[1] = False
      exp[3] = False
      seentimes[:] = []
      is_hover = -1


  if exp[1] and exp[0] != 3*actualwidth//4:
    if int(round(time.time())) not in seentimes:
      seentimes.append(int(round(time.time())))
      if exp[3] == False: exp[3] = True
      else:
        dots.append([exp[0] - (actualwidth//4 + 94), random.randrange(-5, 6)])

  return is_hover, clicked, mpx, mpy, update_render, finished

"""

SUPPLY DEMAND GRAPH

"""

async def prep_sd(screen, actualwidth, actualheight, player):
  top = actualwidth//3 + random.randrange(actualheight//4), actualheight//2 - actualwidth//6 + random.randrange(actualheight//4)
  bottom = 2*actualwidth//3 - random.randrange(actualheight//4), actualheight//2 + actualwidth//6 - random.randrange(actualheight//4)
  top2 = 2*actualwidth//3 - random.randrange(actualheight//4), actualheight//2 - actualwidth//6 + random.randrange(actualheight//4)
  bottom2 = actualwidth//3 + random.randrange(actualheight//4), actualheight//2 + actualwidth//6 - random.randrange(actualheight//4)
  return [top, bottom, top2, bottom2, (actualwidth//4 + 25 + 7, actualheight//2 + actualwidth//4 - 95 - 7)]

async def display_sd(entries, screen, actualwidth, actualheight):
  exp = entries
  pg.draw.line(screen, (0, 255, 0), exp[0], exp[1], 4)
  pg.draw.line(screen, (255, 0, 0), exp[2], exp[3], 4)
  pg.draw.line(screen, (0,0,0), (actualwidth//4 + 25, actualheight//2 - actualwidth//4 + 55), (actualwidth//4 + 25, actualheight//2 + actualwidth//4 - 95), 4)
  pg.draw.line(screen, (0,0,0), (actualwidth//4 + 25, actualheight//2 + actualwidth//4 - 95), (3*actualwidth//4 - 25, actualheight//2 + actualwidth//4 - 95), 4)
  screen.blit(pg.font.Font("OpenSansEmoji.ttf", 50).render("Find the Equilibrium", True, (255, 255, 255)), (385, actualheight//2 - actualwidth//4 + 2))
  screen.blit(pg.font.Font("OpenSansEmoji.ttf", 15).render("Equilibrium (move me)", True, (255, 255, 255)), (exp[4][0]+ 4, exp[4][1] - 11))
  pg.draw.circle(screen, (255, 255, 255), exp[4], 3)

async def eq_sd(entries, screen, actualwidth, actualheight, dmx, dmy, is_hover, clicked):
  finished = False
  exp = entries
  mpx, mpy = pg.mouse.get_pos()
  update_render = False

  if (mpx - exp[4][0])**2 + (mpy - exp[4][1])**2 <= 9:
    if is_hover == -1:
      pg.mouse.set_cursor(*pg.cursors.diamond)
      is_hover = 1

  elif is_hover == 1:
    is_hover = -1
    pg.mouse.set_cursor(*pg.cursors.arrow)

  if any(pg.mouse.get_pressed()):
    exp[4] = [mpx, mpy]

  dx = exp[0][0] - exp[1][0]
  dy = exp[0][1] - exp[1][1]
  slope = dy/dx

  dx2 = exp[2][0] - exp[3][0]
  dy2 = exp[2][1] - exp[3][1]
  slope2 = dy2/dx2


  x = (exp[2][1]-exp[0][1] + slope*exp[0][0] - slope2*exp[2][0])/(slope-slope2)
  y = slope2 * (x - exp[2][0]) + exp[2][1]

  if (x - exp[4][0])**2 + (y - exp[4][1])**2 <= 16:
    pg.mouse.set_cursor(*pg.cursors.arrow)
    finished = True
  #else:
  #  print((x - exp[4][0])**2 + (y - exp[4][1])**2)

  return is_hover, clicked, mpx, mpy, update_render, finished

"""

POWER RULE

"""

async def prep_math(screen, actualwidth, actualheight, player):
  number = ""
  base = 10
  exp = 10
  while base*exp >= 100:
    base = random.randint(1, 10)
    exp = random.randint(3, 10)
  return [base, exp, "", time.time()]

async def display_math(entries, screen, actualwidth, actualheight):
  exp = entries
  base = exp[0]
  expo = exp[1]
  number = exp[2]
  box = pg.Rect(actualwidth//2 - 130, actualheight//2 -20, 260, 40)
  pg.draw.rect(screen, (128, 128, 128), box)
  pg.draw.rect(screen, (255, 255, 255), box, 2)
  screen.blit(pg.font.Font("OpenSansEmoji.ttf", 28).render(f"Find d/dx {base}x^{expo}", True, (0,0,0)), (actualwidth//4 + 35, actualheight//2 - actualwidth//4 + 35))
  if number:
    screen.blit(pg.font.Font("OpenSansEmoji.ttf", 20).render(number, True, (0,0,255)), (actualwidth//2 - 130 + 3, actualheight//2 - 20 + 3))
  
async def do_math(entries, screen, actualwidth, actualheight, dmx, dmy, is_hover, clicked):
  finished = False
  exp = entries
  mpx, mpy = pg.mouse.get_pos()
  update_render = False
  keys = pg.key.get_pressed()
  if time.time() - entries[3] > 0.1:
    if keys[K_x] and len(exp[2]) < 7:
      entries[3] = time.time()
      exp[2] += "x"
    elif (keys[K_LSHIFT] or keys[K_RSHIFT]) and keys[K_6] and len(exp[2]) < 7:
      entries[3] = time.time()
      exp[2] += "^"
    elif keys[K_BACKSPACE]: 
      entries[3] = time.time()
      exp[2] = exp[2][:-1]
    elif any([keys[i] for i in list(range(48, 58)) + [K_BACKSPACE]]) and len(exp[2]) < 7:
      entries[3] = time.time()
      for i in range(48, 58):
        if keys[i]:
          exp[2] += str(i - 48)
          break
    shouldsee = f"{exp[0]*exp[1]}x^{exp[1]-1}"
    if exp[2].lower() == shouldsee:
      finished = True

  return is_hover, clicked, mpx, mpy, update_render, finished

"""

INVERSE POWER RULE

"""

async def prep_math2(screen, actualwidth, actualheight, player):
  number = ""
  base = 10
  exp = 3
  while not (base/(exp+1)).is_integer() or int(round(base/(exp+1))) == 1:
    base = random.randint(1, 10)
    exp = random.randint(2, 9)
  return [base, exp, "", time.time()]

async def display_math2(entries, screen, actualwidth, actualheight):
  exp = entries
  base = exp[0]
  expo = exp[1]
  number = exp[2]
  box = pg.Rect(actualwidth//2 - 130, actualheight//2 -20, 260, 40)
  pg.draw.rect(screen, (128, 128, 128), box)
  pg.draw.rect(screen, (255, 255, 255), box, 2)
  screen.blit(pg.font.Font("OpenSansEmoji.ttf", 28).render(f"Find ∫{base}x^{expo} dx", True, (0,0,0)), (actualwidth//4 + 35, actualheight//2 - actualwidth//4 + 35))
  if number:
    screen.blit(pg.font.Font("OpenSansEmoji.ttf", 20).render(number, True, (0,0,255)), (actualwidth//2 - 130 + 3, actualheight//2 - 20 + 3))
  
async def do_math2(entries, screen, actualwidth, actualheight, dmx, dmy, is_hover, clicked):
  finished = False
  exp = entries
  mpx, mpy = pg.mouse.get_pos()
  update_render = False
  keys = pg.key.get_pressed()
  if time.time() - entries[3] > 0.1:
    if keys[K_x] and len(exp[2]) < 9:
      entries[3] = time.time()
      exp[2] += "x"
    elif keys[K_EQUALS] and len(exp[2]) < 9:
      entries[3] = time.time()
      exp[2] += "+"
    elif keys[K_c] and len(exp[2]) < 9:
      entries[3] = time.time()
      exp[2] += "c"
    elif (keys[K_LSHIFT] or keys[K_RSHIFT]) and keys[K_6] and len(exp[2]) < 9:
      entries[3] = time.time()
      exp[2] += "^"
    elif keys[K_BACKSPACE]: 
      entries[3] = time.time()
      exp[2] = exp[2][:-1]
    elif any([keys[i] for i in list(range(48, 58)) + [K_BACKSPACE]]) and len(exp[2]) < 9:
      entries[3] = time.time()
      for i in range(48, 58):
        if keys[i]:
          exp[2] += str(i - 48)
          break
    shouldsee = f"{exp[0]//(exp[1]+1)}x^{exp[1]+1}+c"
    if exp[2].lower() == shouldsee:
      finished = True

  return is_hover, clicked, mpx, mpy, update_render, finished

"""

LIST SORT

"""

async def prep_list(screen, actualwidth, actualheight, player):
  numbers = random.sample(range(1000), 10)
  return numbers, [None, time.time()]

async def display_list(entries, screen, actualwidth, actualheight):
  numbers, clicked = entries
  x = actualwidth//4 + 10
  screen.blit(pg.font.Font("OpenSansEmoji.ttf", 28).render(f"Sort list in ascending order", True, (0,0,0)), (actualwidth//4 + 35, actualheight//2 - actualwidth//4 + 35))
  for number in numbers:
    if clicked[0] and numbers[clicked[0]] == number: 
      col = (255, 255, 255)
    else: col = (128, 128, 128)
    pg.draw.rect(screen, col, pg.Rect(x, actualheight//2, 65, 65))
    screen.blit(pg.font.Font("OpenSansEmoji.ttf", 28).render(str(number), True, (0,0,0)), (x + 10, actualheight//2 + 15))
    x += 75
  
async def do_list(entries, screen, actualwidth, actualheight, dmx, dmy, is_hover, clicked):
  finished = False
  numbers, click = entries
  mpx, mpy = pg.mouse.get_pos()
  update_render = False

  xfloor = (((mpx-(actualwidth//4 + 10))//75) * 75) + actualwidth//4 + 10
  if mpy >= actualheight//2 and mpy < actualheight//2 + 65 and mpx >= xfloor and mpx < xfloor + 65 and (mpx-(actualwidth//4 + 10))//75 in range(10):
    if is_hover != (mpx-(actualwidth//4 + 10))//75:
      is_hover = (mpx-(actualwidth//4 + 10))//75
      pg.mouse.set_cursor(*pg.cursors.diamond)

  elif is_hover != -1:
    pg.mouse.set_cursor(*pg.cursors.arrow)
    is_hover = -1

  if any(pg.mouse.get_pressed()) and is_hover != -1 and time.time() - click[1] > 0.1:
    if is_hover == click[0]:
      click[0] = None
    elif click[0] == None:
      click[0] = is_hover
    else:
      numbers[is_hover], numbers[click[0]] = numbers[click[0]], numbers[is_hover]
      click[0] = None
      
    click[1] = time.time()

  if all([numbers[i] < numbers[i+1] for i in range(len(numbers)-1)]):
    finished = True

  return is_hover, clicked, mpx, mpy, update_render, finished

"""

PAINT E

"""

async def prep_e(screen, actualwidth, actualheight, player):
  colors = [[random.randint(0, 255) for i in range(3)] for j in range(8)] + [[255, 255, 255], [255, 0, 0]]
  random.shuffle(colors)
  return colors, [random.randint(0, 255) for i in range(3)], [random.randint(0, 255) for i in range(3)], [0, time.time()]

async def display_e(entries, screen, actualwidth, actualheight):
  colors, base, letter, exp = entries
  baseimg = pg.image.load("sprites/e_base.png").convert_alpha()
  baseimg.fill(base, special_flags=pg.BLEND_RGB_MULT)
  letimg = pg.image.load("sprites/e_letter.png").convert_alpha()
  letimg.fill(letter, special_flags=pg.BLEND_RGB_MULT)
  screen.blit(baseimg, (actualwidth//4 + 1, actualheight//2 - (actualwidth//4 - 1)))
  screen.blit(letimg, (actualwidth//4 + 1, actualheight//2 - (actualwidth//4 - 1)))
  x = actualwidth//4 + 10
  for color in colors:
    if colors[exp[0]] == color: 
      col = (0, 0, 255)
    else: col = (0,0,0)
    pg.draw.rect(screen, col, pg.Rect(x, actualheight//2 - actualwidth//4 + 2, 65, 65))
    pg.draw.rect(screen, color, pg.Rect(x+3, actualheight//2 - actualwidth//4 + 2+3, 59, 59))
    x += 75

async def paint_e(entries, screen, actualwidth, actualheight, dmx, dmy, is_hover, clicked):
  finished = False
  colors, base, letter, exp = entries
  mpx, mpy = pg.mouse.get_pos()
  update_render = False
  baseimg = pg.Surface((actualwidth, actualheight), pg.SRCALPHA)
  baseimg.blit(pg.image.load("sprites/e_base.png").convert_alpha(), (actualwidth//4+1, actualheight//2 - actualwidth//4 + 1))
  letimg = pg.Surface((actualwidth, actualheight), pg.SRCALPHA)
  letimg.blit(pg.image.load("sprites/e_letter.png").convert_alpha(), (actualwidth//4+1, actualheight//2 - actualwidth//4 + 1))
  xfloor = (((mpx-(actualwidth//4 + 10))//75) * 75) + actualwidth//4 + 10
  if mpy >= actualheight//2-actualwidth//4+2 and mpy < actualheight//2-actualwidth//4+2+65 and mpx >= xfloor and mpx < xfloor + 65 and (mpx-(actualwidth//4 + 10))//75 in range(10):
    if is_hover != (mpx-(actualwidth//4 + 10))//75:
      is_hover = (mpx-(actualwidth//4 + 10))//75
      pg.mouse.set_cursor(*pg.cursors.diamond)

  elif letimg.get_at((mpx, mpy))[0] == 255:
    is_hover = -2
    pg.mouse.set_cursor(*pg.cursors.diamond)

  elif baseimg.get_at((mpx, mpy))[0] == 255 and letimg.get_at((mpx, mpy)) != (0,0,0,255):
    is_hover = -3
    pg.mouse.set_cursor(*pg.cursors.diamond)

  elif is_hover != -1:
    pg.mouse.set_cursor(*pg.cursors.arrow)
    is_hover = -1

  if any(pg.mouse.get_pressed()) and time.time() - exp[1] > 0.1:
    if is_hover not in [-1, -2, -3]:
      exp[0] = is_hover  
      exp[1] = time.time()
    elif is_hover == -2:
      letter[:] = colors[exp[0]][:]
      exp[1] = time.time()
    elif is_hover == -3:
      base[:] = colors[exp[0]][:]
      exp[1] = time.time()

    if base == [255, 255, 255] and letter == [255, 0, 0]:
      finished = True
      pg.mouse.set_cursor(*pg.cursors.arrow)

  return is_hover, clicked, mpx, mpy, update_render, finished

"""

FEED BIRB

"""

async def prep_birb(screen, actualwidth, actualheight, player):
  return [0, 0, actualwidth//4+30, actualheight//2+actualwidth//4-95, time.time(), -1, -1, False, 0]

async def display_birb(entries, screen, actualwidth, actualheight):
  vix, viy, x, y, thetime, mx, my, flying, ydir = entries
  crow = pg.image.load("sprites/crow.png")
  crow = pg.transform.flip(crow, True, False)
  crow = pg.transform.scale(crow, (100, 100))
  screen.blit(crow, (3*actualwidth//4-100, actualheight//2+actualwidth//4-130))
  #pg.draw.rect(screen, (0,0,255), pg.Rect(actualwidth//2, actualheight//2, 20, actualwidth//4))
  pg.draw.rect(screen, (0,0,255), pg.Rect(3*actualwidth//4-63, actualheight//2+actualwidth//4-30, 20, 30))
  pg.draw.rect(screen, (0,0,255), pg.Rect(actualwidth//4+20, actualheight//2+actualwidth//4-80, 20, 80))
  if mx != -1:
    pg.draw.line(screen, (255, 255, 255, 128), (mx, my), (actualwidth//4+30, actualheight//2+actualwidth//4-95), 5)
  pg.draw.circle(screen, (194, 172, 110), (x, y), 15)


async def feed_birb(entries, screen, actualwidth, actualheight, dmx, dmy, is_hover, clicked):
  vix, viy, x, y, thetime, mx, my, flying, ydir = entries
  mpx, mpy = pg.mouse.get_pos()
  update_render = False
  finished = False

  ctrx = actualwidth//4+30
  ctry = actualheight//2+actualwidth//4-95

  if (mpx - ctrx)**2 + (mpy - ctry)**2 <= 255:
    if is_hover == -1:
      is_hover = 1
      pg.mouse.set_cursor(*pg.cursors.diamond)

  elif is_hover == 1:
    is_hover = -1
    pg.mouse.set_cursor(*pg.cursors.arrow)

  if flying:
    diff = time.time() - thetime
    entries[2] = entries[2] + entries[0]
    entries[3] = ctry + int(round(entries[1]*diff + ydir*-9.81*0.5*diff*diff))
    if entries[3] == 0: 
      entries[:] = [0, 0, actualwidth//4+30, actualheight//2+actualwidth//4-95, time.time(), -1, -1, False, 0]
    elif entries[2] >= 3*actualwidth//4 or entries[2] <= actualwidth//4 or screen.get_at((entries[2], entries[3])) == (0,0,255,255):
      entries[:] = [0, 0, actualwidth//4+30, actualheight//2+actualwidth//4-95, time.time(), -1, -1, False, 0]
    elif entries[3] <= actualheight//2 - actualwidth//4 + 1 or entries[3] >= actualheight//2 + actualwidth//4:
      entries[:] = [0, 0, actualwidth//4+30, actualheight//2+actualwidth//4-95, time.time(), -1, -1, False, 0]
    
    update_render = True

  if (x - 1053)**2 + (y-678)**2 <= 1000:
    finished = True
    pg.mouse.set_cursor(*pg.cursors.arrow)

  if any(pg.mouse.get_pressed()) and is_hover != -1:
    is_hover = 2
    entries[5] = mpx
    entries[6] = mpy
      
  elif not any(pg.mouse.get_pressed()) and is_hover == 2:
    is_hover = -1
    pg.mouse.set_cursor(*pg.cursors.arrow)
    entries[7] = True
    entries[4] = time.time()
    entries[0] = (ctrx - mpx)//5
    entries[1] = (ctry - mpy)*2
    entries[5] = -1
    entries[6] = -1

  return is_hover, clicked, mpx, mpy, update_render, finished
