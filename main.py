# test map: Map data © OpenStreetMap contributors; openstreetmap.org

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

import numpy as np

pg.init()
pg.display.set_caption("Academia")

font = pg.font.Font("OpenSansEmoji.ttf", 70)
font2 = pg.font.Font("OpenSansEmoji.ttf", 30)
font3 = pg.font.Font("OpenSansEmoji.ttf", 20)
font4 = pg.font.Font("OpenSansEmoji.ttf", 40)

font5 = pg.font.Font("OpenSansEmoji.ttf", 100)

size = width, height = 1536, 801
screen = pg.display.set_mode(size, pg.RESIZABLE)
toshow = pg.image.load("sprites/book.png").convert_alpha()
pg.display.set_icon(toshow)

def fnt(num):
  return pg.font.Font("OpenSansEmoji.ttf", num)

def rtext(font, text, y, x = "center", color = (255, 255, 255), d = True, ctr = False):
  global screen, size, width, height
  if x == "center":
    length = font.size(text)[0]//2
    x = width//2 - length
  if ctr:
    length = font.size(text)[0]//2
    x -= length
  if d:
    screen.blit(font.render(text, True, (0,0,0)), (x-2, y+2))
  screen.blit(font.render(text, True, color), (x, y))

rtext(font, "Loading...", height//2 - 35)
pg.display.flip()

def textbox(y, x = "default", text = "", col = (255, 255, 255), wdth = 260, textcol = (255, 255, 255), myfont = font3):
  global screen, width, height, font, font2
  if x == "default":
    x = width//2
  box = pg.Rect(x, y-3, wdth, 40)
  pg.draw.rect(screen, (128, 128, 128), box)
  pg.draw.rect(screen, col, box, 2)
  if text:
    rtext(myfont, text, y, x+5, color = textcol)

def load(image, x = -1, y = -1, bound = False):
  for event in pg.event.get():
    if event.type == QUIT: 
      sys.exit()
  img = pg.image.load(image).convert_alpha()
  if x != -1:
    img = pg.transform.scale(img, (x, y))
  if bound:
    baseline = pg.Surface((5494, 6106), pg.SRCALPHA)
    baseline.fill((0,0,0,0))
    baseline.blit(img, (100, 100))
    return baseline
  return img

def half(image):
  return pg.transform.scale(image, (image.get_width()//2, image.get_height()//2))

for file in os.listdir("assets"):
  for event in pg.event.get():
    if event.type == QUIT: 
      sys.exit()
  globals()[file.split(".")[0]] = load(f"assets/{file}")

saved = [load(f"circles/{i}.png") for i in range(101)]

for event in pg.event.get():
  if event.type == QUIT: 
    sys.exit()

def display_menu():
  global size, width, height, font, font2
  basemenu = load("basemenu.JPG", width, 3*width//4)
  screen.blit(basemenu, (0,height-3*width//4))

  rtext(font, "Academia", 20, 5)
  rtext(font2, "It's got an even better name now. ©2020-2021 Bright Universe", height-40)

def nmap(val, omin, omax, rmin, rmax):
  return (float(val) - float(omin)) * (float(rmax) - float(rmin)) / (float(omax) - float(omin)) + float(rmin)

pwidth = 100
pheight = 150

MS = 3

pwidth2 = 16*MS
pheight2 = 25*MS

actualwidth = 1536
actualheight = 801

def pscale(player, x, y, col, rgb = False, transp = 0):
  global size, width, height, actualwidth, actualheight
  dx = nmap(x, 0, actualwidth, 0, width)
  dy = nmap(y, 0, actualheight, 0, height)
  mx = nmap(player.get_width(), 0, actualwidth, 0, width)
  my = nmap(player.get_height(), 0, actualheight, 0, height)
  pl = pg.transform.scale(player, (int(round(mx)), int(round(my))))
  if rgb:
    pl.fill(col, special_flags=pg.BLEND_RGB_MULT)
  else:
    outputs = colorsys.hls_to_rgb(col[0]/360, col[2]/100, col[1]/100)
    pl.fill((outputs[0]*255, outputs[1]*255, outputs[2]*255), special_flags=pg.BLEND_RGB_MULT)
  if transp:
    pl = pl.copy()
    pl.fill((255, 255, 255, 128), None, pg.BLEND_RGBA_MULT)
  screen.blit(pl, (int(round(dx)), int(round(dy))))

myusername = None

from taskmod import *

tasks = []
for i in range(256):
  if i in [1, 128]:
    tasks.append(load(f"maps/tasks/{i}.png", bound = True))
  else: tasks.append(None)

mainmap = load("maps/ubc.png", bound = True)
prime = taskbase(actualwidth, actualheight)

def fade():
  global screen
  for i in range(400):
    for event in pg.event.get():
      if event.type == QUIT: 
        sys.exit()
    surf = pg.Surface((screen.get_width(), screen.get_height()), pg.SRCALPHA)
    surf.fill((0, 0, 0, 5))
    screen.blit(surf, (0,0))
    pg.display.flip()

def delay(s):
  a = time.time()
  while time.time() - a < s:
    for event in pg.event.get():
      if event.type == QUIT: 
        sys.exit()

async def play(websocket, pdict, is_owner):
  global screen, size, width, height, myusername, actualwidth, actualheight

  if is_owner:
    await websocket.send("start")
    res = await websocket.recv()
    for entry in json.loads(res):
      # handle the player change appearance thing later
      if entry[0] == "Players":
        for player in entry[1]:
          for key in entry[1][player]:
            pdict[player][key] = entry[1][player][key]
    
  await websocket.send("force")
  res = await websocket.recv()
  d = json.loads(res)
  for entry in d:
    for key in d[entry]:
      pdict[entry][key] = d[entry][key]
  
  if len(pdict) > 1:
    numbrc = (len(pdict) + 3)//10 + 1
  else: numbrc = 0
  fade()
  delay(0.5)
  rtext(fnt(200), ["Student", "BRC"][pdict[myusername]["impostor"]], actualheight//2 - 210, color = [(255, 255, 255), (255, 0, 0)][pdict[myusername]["impostor"]])
  rtext(fnt(70), f"{numbrc} BRC lurk{['s', ''][numbrc != 1]} in the shadows...", actualheight//2 + 10)
  pg.display.flip()
  delay(2)

  offsetx = (pdict[myusername]["x"]*MS - width//2)
  offsety = (pdict[myusername]["y"]*MS - height//2)
  ox = (pdict[myusername]["x"] - width//2)
  oy = (pdict[myusername]["y"] - height//2)

  screen.fill((0,0,0))
  temp = pg.Surface((width, height))
  temp.blit(mainmap, (0,0), pg.Rect(ox, oy, width, height))
  temp = pg.transform.scale(temp, (width*MS, height*MS))
  screen.blit(temp, (0,0), pg.Rect(width, height, width, height))

  player = load("player.png", pwidth2, pheight2)
  reverseplayer = pg.transform.flip(player, True, False)
  pwalking = load("playerwalkingfront.png", pwidth2, pheight2)
  reversepwalking = pg.transform.flip(pwalking, True, False)
  pwalkingb = load("playerwalkingback.png", pwidth2, pheight2)
  reversepwalkingb = pg.transform.flip(pwalkingb, True, False)

  oof = load("oof.png", pheight2, pwidth2)

  fsize = nmap(40, 0, actualwidth, 0, width)
  thefont = pg.font.Font("OpenSansEmoji.ttf", int(round(fsize)))
  for entry in pdict:
    e = pdict[entry]
    e["f"] = 0
    e["f2"] = 0
    if e["x"]*MS in range(offsetx, offsetx + width) and e["y"]*MS in range(offsety, offsety + height):
      pscale(player, e["x"]*MS-pwidth2//2 - offsetx, e["y"]*MS-pheight2//2 - offsety, (e["h"], e["s"], e["l"]), transp = e["ghost"])
      my = nmap(e["y"]*MS-50-pheight2//2 - offsety, 0, actualheight, 0, height)
      mx = nmap(e["x"]*MS - offsetx, 0, actualwidth, 0, width)
      rtext(thefont, e["nickname"], int(round(my)), int(round(mx)), color = (128,128,128), ctr = True)

  tasknames = pdict[myusername]["tasks"]
  total = len(tasknames) * len([p for p in pdict if not pdict[p]["impostor"]])
  complete = sum([sum([1 for t in pdict[u]["tasks"] if pdict[u]["tasks"][t]]) for u in pdict if not pdict[u]["impostor"]])

  by = 42
  results = {}
  ltext = f"TODO ({round(complete*100/total)}% total)"
  except: ltext = "TODO (100% total)"
  maxwidth = font4.size(ltext)[0] + 4
  if not pdict[myusername]["impostor"]:
    for tsk in tasknames:
      result = taskdesc[int(tsk)]
      if tasknames[tsk]: result += " (Complete)"
      results[tsk] = result
      if font3.size(result)[0] + 4 > maxwidth:
        maxwidth = font3.size(result)[0] + 4

    tasklist = pg.Surface((maxwidth, len(tasknames)*25 + 40), pg.SRCALPHA)
    tasklist.fill((255, 255, 255, 220))
    screen.blit(tasklist, (2, 2))
    screen.blit(font4.render(ltext, True, (0,0,0)), (2, 2))
    for tsk in tasknames:
      screen.blit(font3.render(results[tsk], True, [(215, 146, 146), (136, 255, 136)][tasknames[tsk]]), (2, by))
      by += 25

  else:
    tasklist = pg.Surface((maxwidth, 2*25 + 40), pg.SRCALPHA)
    tasklist.fill((255, 255, 255, 220))
    screen.blit(tasklist, (2, 2))
    screen.blit(font4.render(ltext, True, (0,0,0)), (2, 2))
    screen.blit(font3.render("Ruin everyone as BRC.", True, (215, 146, 146)), (2, by))
    by += 25
    diff = max(0, round(pdict[myusername]["killcooldown"] + 0 - time.time()))
    if diff == 0: phr = "You can beam now."
    else: phr = f"You can beam again in {diff}s."
    screen.blit(font3.render(phr, True, (215, 146, 146)), (2, by))

  pg.display.flip()
  whichleg = True
  task = 255
  doing_task = False
  completed = [0, 255]

  base = time.time()
  relevant_entries = None

  is_hover = -1
  dmx, dmy = pg.mouse.get_pos()
  clicked = False

  meeting_called = 0
  textinput = ""
  flag = True
  flg = False
  return_pressed = False

  playerstoadd = None

  storage = []

  curnum = -1
  whodidit = None
  should_vote = False
  kick_player = False

  endtime = 0

  voted = {}
  bipflag = False
  lastx = 0
  lasty = 0
  globalminname = None
  globalminrep = None
  globalkcool = 0
  globalitems = []

  while True:
    keys = pg.key.get_pressed()
    spacestate = 0
    for event in pg.event.get():
      if event.type == QUIT: 
        sys.exit()
      elif event.type == VIDEORESIZE:
        size = width, height = (event.w, event.h)
        screen = pg.display.set_mode(size, pg.RESIZABLE)
        flag = True
        pg.display.flip()
      elif event.type == KEYDOWN:
        if event.key == K_SPACE:
          spacestate = 1
        if event.key == K_BACKSPACE and meeting_called == 3:
          textinput = textinput[:-1]
          textbox(height - 70, 2*width//3 + 30, wdth = 440, col = (114, 247, 247), text = textinput, myfont = fnt(15))
          pg.display.flip()
        elif event.unicode not in ",{}[]|\\\r" and meeting_called == 3:
          if keys[K_RSHIFT] or keys[K_LSHIFT]:
            textinput += event.unicode.upper()
          else:
            textinput += event.unicode
          if fnt(15).size(textinput)[0] > 438 or len(textinput) > 100:
            textinput = textinput[:-1]
          textbox(height - 70, 2*width//3 + 30, wdth = 440, col = (114, 247, 247), text = textinput, myfont = fnt(15))
          pg.display.flip()
      elif event.type == MOUSEBUTTONUP and meeting_called == 3 and curnum in range(len(playerstoadd)+1) and (curnum == len(playerstoadd) or not pdict[playerstoadd[curnum]]["ghost"]):
        should_vote = True

    if keys[K_TAB] and is_owner:
      await websocket.send("finish")
      res = await websocket.recv()
      return [res, is_owner]
    if keys[K_ESCAPE]:
      await websocket.send("leave")
      await websocket.recv()
      break

    if keys[K_RETURN] and meeting_called == 3:
      return_pressed = True

    if spacestate and meeting_called == 0 and task == 1 and not pdict[myusername]["ghost"]:
      meeting_called = 1

    elif keys[K_q] and pdict[myusername]["impostor"] and not pdict[myusername]["ghost"] and globalminname and time.time() > pdict[myusername]["killcooldown"] + globalkcool:
      await websocket.send(f"kek,{globalminname['username']}")
      res = await websocket.recv()
      res = json.loads(res)
      pdict[myusername]["killcooldown"] = res[0]
      globalkcool = res[1]
      pdict[globalminname['username']]["ghost"] = 1
      globalitems.append(res[2])
      pdict[myusername]["x"] = pdict[globalminname['username']]["x"]
      pdict[myusername]["y"] = pdict[globalminname['username']]["y"]

    elif keys[K_r] and meeting_called == 0 and not pdict[myusername]["ghost"] and globalminrep:
      meeting_called = 0.5

    if doing_task:
      mpx, mpy = pg.mouse.get_pos()
      def collide(x, y):
        return x >= 3*actualwidth//4 - 32 and x <= 3*actualwidth//4 and y >= actualheight//2-actualwidth//4 and y <= actualheight//2-actualwidth//4 + 32
      
      if keys[K_DOWN] or keys[K_UP] or keys[K_LEFT] or keys[K_RIGHT]:
        is_hover = -1
        clicked = False
        flag = True
        relevant_entries = None
        doing_task = False
      else:
        is_hover, clicked, dmx, dmy, update_render, finished = await globals()[inputs[task]](relevant_entries, screen, actualwidth, actualheight, dmx, dmy, is_hover, clicked)
        if finished:
          await websocket.send(f"task,{task}")
          res = await websocket.recv()
          pdict[myusername]["tasks"][str(task)] = True
          is_hover = -1
          clicked = False
          flag = True
          relevant_entries = None
          doing_task = False
          completed.append(task)
        elif update_render:
          flag = True

    if meeting_called == 3:
      mpx, mpy = pg.mouse.get_pos()
      rightborder = 2*actualwidth//3
      acceptstart = (((mpx - 10)// (rightborder // 5)) * rightborder//5 + 10)
      acceptend = acceptstart + rightborder//5 - 3

      acceptstart2 = (mpy - 10)//37 * 37 + 10
      acceptend2 = acceptstart2 + 33

      if not pdict[myusername]["ghost"] and mpx in range(acceptstart, acceptend) and mpy in range(acceptstart2, acceptend2) and (mpy - 10)//37 in range(20) and (mpx - 10)//(rightborder//5) in range(5):
        num = 20*((mpx - 10)//(rightborder//5)) + (mpy - 10)//37
        if num in range(len(playerstoadd)) and not pdict[playerstoadd[num]]["ghost"]:
          if num != curnum:
            pg.mouse.set_cursor(*pg.cursors.diamond)
            curnum = num
            flg = True
        elif num == len(playerstoadd):
          if num != curnum:
            pg.mouse.set_cursor(*pg.cursors.diamond)
            curnum = num
            flg = True
        else:
          if num != curnum:
            pg.mouse.set_cursor(*pg.cursors.arrow)
            curnum = num
            flg = True

      elif curnum != -1:
        curnum = -1
        pg.mouse.set_cursor(*pg.cursors.arrow)
        flg = True

      if flg:
        rightborder = 2*actualwidth//3
        playerstoadd = list(pdict.keys())
        i = 0
        for x in range(5):
          for pos in range(20):
            call = False
            col = [200, 200, 200]
            if i < len(playerstoadd) and playerstoadd[i] == whodidit:
              col = [252, 186, 3]
              call = True
            if myusername in voted:
              if i < len(playerstoadd) and voted[myusername] == playerstoadd[i]:
                if voted[myusername] == whodidit:
                  col = [226, 235, 52]
                else: col = [97, 235, 52]
              elif i == len(playerstoadd) and voted[myusername] == "skip":
                col = [97, 235, 52]
            if i == curnum and i <= len(playerstoadd):
              col = [min(255, k + 20) for k in col]
            if i < len(playerstoadd) and pdict[playerstoadd[i]]["ghost"]: col = [255, 0, 0]
            pg.draw.rect(screen, col, pg.Rect(x*rightborder//5 + 10, pos*37 + 10, rightborder//5 - 3, 33))
            extra = ""
            if call:
              extra += "(Called) "
            if i < len(playerstoadd) and playerstoadd[i] in voted:
              extra += "(VOTED) "
            if extra:
              screen.blit(pg.font.Font("OpenSansEmoji.ttf", 10).render(extra, True, (0,0,0)), (x*rightborder//5 + 34, pos*37 + 28))
            if i < len(playerstoadd):
              e = pdict[playerstoadd[i]]
              pscale(pg.transform.scale(player, (20, 30)), x*rightborder//5 + 11, pos*37 + 11, (e["h"], e["s"], e["l"]), transp = e["ghost"])
              screen.blit(pg.font.Font("OpenSansEmoji.ttf", 15).render(e["nickname"], True, (0,0,0)), (x*rightborder//5 + 34, pos*37 + 12))
              i+= 1
            elif i == len(playerstoadd):
              screen.blit(pg.font.Font("OpenSansEmoji.ttf", 15).render("Skip Vote", True, (0,0,0)), (x*rightborder//5 +  12, pos*37 + 12))
              i += 1

      pr = f"Time Remaining: {round(endtime - time.time())}s"
      pg.draw.rect(screen, (255, 255, 255), pg.Rect(actualwidth//2 - fnt(20).size(pr)[0]//2 - 100, actualheight - 35, fnt(20).size(pr)[0] + 200, 30))
      if round(endtime - time.time()) < 0:
        kick_player = True
      else:
        screen.blit(fnt(20).render(pr, True, (255, 0, 0)), (actualwidth//2 - fnt(20).size(pr)[0]//2, actualheight-35))
      pg.display.flip()
      flg = False
      
    if spacestate and task not in completed and not doing_task and task != 1 and not pdict[myusername]["impostor"]:
      doing_task = True
      relevant_entries = await globals()[prep[task]](screen, actualwidth, actualheight)
      flag = True

    if time.time() - base >= 0.07 or flag:
      if time.time() - base >= 0.07:
        if doing_task: payload = f"move,0,0,0,0,0"
        elif meeting_called == 1: 
          payload = "emergency"
          meeting_called = 2
        elif meeting_called == 0.5:
          payload = f"report,{globalminrep['x']},{globalminrep['y']}"
          meeting_called = 2
        elif should_vote and meeting_called == 3 and not pdict[myusername]["ghost"]:
          should_vote = False
          vote = playerstoadd + ["skip"]
          payload = f"vote,{vote[curnum]}"
        elif meeting_called == 3 and len(textinput) and return_pressed:
          return_pressed = False
          payload = f"chat,{textinput}"
          textinput = ""    
          textbox(height - 70, 2*width//3 + 30, wdth = 440, col = (114, 247, 247), text = "", myfont = fnt(15))  
        else: payload = f"move,{keys[K_DOWN]},{keys[K_UP]},{keys[K_LEFT]},{keys[K_RIGHT]},{spacestate}"
        await websocket.send(payload)
        
        if meeting_called != 3:
            ofx = (16/2) * (keys[K_RIGHT] - keys[K_LEFT])
            ofy = (16/2) * (keys[K_DOWN] - keys[K_UP])
            if (keys[K_DOWN] or keys[K_UP] or keys[K_LEFT] or keys[K_RIGHT]) \
              and (lastx == pdict[myusername]["x"]) and (lasty == pdict[myusername]["y"]):
                  ofx = 0
                  ofy = 0
            lastx = pdict[myusername]["x"]
            lasty = pdict[myusername]["y"]

            px = pdict[myusername]["x"] + ofx
            py = pdict[myusername]["y"] + ofy
            offsetx = (px*MS - width//2)
            offsety = (py*MS - height//2)

            ox = (px - width//2)
            oy = (py - height//2)
            by = 42

            screen.fill((0,0,0))
            temp = pg.Surface((width, height))
            temp.blit(mainmap, (0,0), pg.Rect(ox, oy, width, height))
            temp = pg.transform.scale(temp, (width*MS, height*MS))
            screen.blit(temp, (0,0), pg.Rect(width, height, width, height))

            if task not in completed and (not pdict[myusername]["ghost"] or task != 1) and (not pdict[myusername]["impostor"] or task == 1):
                overmap = tasks[task]
                temp = pg.Surface((width, height), pg.SRCALPHA)
                temp.blit(overmap, (0,0), pg.Rect(ox, oy, width, height))
                temp = pg.transform.scale(temp, (width*MS, height*MS))
                screen.blit(temp, (0,0), pg.Rect(width, height, width, height))

            for e in globalitems:
              pscale(oof, e["x"]*MS-oof.get_width()//2 - offsetx, e["y"]*MS-oof.get_width()//2 - offsety, (e["h"], e["s"], e["l"]))

            for opt in pdict:
                e = pdict[opt]
                ex = None
                ey = None
                if not pdict[myusername]["ghost"] and e["ghost"]: continue
                if opt == myusername:
                    ex = e["x"] + ofx
                    ey = e["y"] + ofy
                else:
                    ex = e["x"]
                    ey = e["y"]
                    
                if e["f2"] > 0:
                  todo = 1+whichleg
                else: todo = 0
                result = [[reverseplayer, player], [reversepwalking, pwalking], [reversepwalkingb, pwalkingb]][todo][e["f"]]
                pscale(result, ex*MS-pwidth2//2 - offsetx, ey*MS-pheight2//2 - offsety, (e["h"], e["s"], e["l"]), transp = e["ghost"])
                my = nmap(ey*MS-50-pheight2//2 - offsety, 0, actualheight, 0, height)
                mx = nmap(ex*MS - offsetx, 0, actualwidth, 0, width)
                rtext(thefont, pdict[opt]["nickname"], int(round(my)), int(round(mx)), color = (128,128,128), ctr = True)

            tasknames = pdict[myusername]["tasks"]
            total = len(tasknames) * len([p for p in pdict if not pdict[p]["impostor"]])
            complete = sum([sum([1 for t in pdict[u]["tasks"] if pdict[u]["tasks"][t]]) for u in pdict if not pdict[u]["impostor"]])

            by = 42
            results = {}
            ltext = f"TODO ({round(complete*100/total)}% total)"
            except: ltext = "TODO (100% total)"
            maxwidth = font4.size(ltext)[0] + 4
            if not pdict[myusername]["impostor"]:
              for tsk in tasknames:
                result = taskdesc[int(tsk)]
                if tasknames[tsk]: result += " (Complete)"
                results[tsk] = result
                if font3.size(result)[0] + 4 > maxwidth:
                  maxwidth = font3.size(result)[0] + 4

              tasklist = pg.Surface((maxwidth, len(tasknames)*25 + 40), pg.SRCALPHA)
              tasklist.fill((255, 255, 255, 220))
              screen.blit(tasklist, (2, 2))
              screen.blit(font4.render(ltext, True, (0,0,0)), (2, 2))
              for tsk in tasknames:
                screen.blit(font3.render(results[tsk], True, [(215, 146, 146), (136, 255, 136)][tasknames[tsk]]), (2, by))
                by += 25

            else:
              tasklist = pg.Surface((maxwidth, 2*25 + 40), pg.SRCALPHA)
              tasklist.fill((255, 255, 255, 220))
              screen.blit(tasklist, (2, 2))
              screen.blit(font4.render(ltext, True, (0,0,0)), (2, 2))
              screen.blit(font3.render("Ruin everyone as BRC.", True, (215, 146, 146)), (2, by))
              by += 25
              diff = max(0, round(pdict[myusername]["killcooldown"] + globalkcool - time.time()))
              if diff == 0: phr = "You can beam now."
              else: phr = f"You can beam again in {diff}s."
              screen.blit(font3.render(phr, True, (215, 146, 146)), (2, by))

            minimum = math.inf
            minname = None
            if pdict[myusername]["impostor"] and round(pdict[myusername]["killcooldown"] + globalkcool - time.time()) <= 0:
              a = pdict[myusername]
              for opt in pdict:
                if opt == myusername or pdict[opt]["ghost"]: continue
                b = pdict[opt]
                dist = (a["x"] - b["x"])**2 + (a["y"] - b["y"])**2
                if dist < a["krange"]**2 and dist < minimum:
                  minimum = dist
                  minname = b

            minrep = math.inf
            namerep = None
            if not pdict[myusername]["ghost"]:
              a = pdict[myusername]
              for b in globalitems:
                dist = (a["x"] - b["x"])**2 + (a["y"] - b["y"])**2
                if dist < 48**2 and dist < minrep:
                  minrep = dist
                  namerep = b

            globalminname = minname
            globalminrep = namerep

            pg.draw.rect(screen, (128, 128, 128), pg.Rect(actualwidth//2 - 300, actualheight - 100, 600, 70))
            has = False
            if globalminrep and not pdict[myusername]["ghost"]:
              has = True
              rtext(fnt(30), "Press R to report", actualheight - 98)
            if task == 1 and not pdict[myusername]["ghost"] and not has:
              rtext(fnt(30), "Press SPACE to call meeting", actualheight - 98)
              has = True
            elif task not in [0, 1, 255] and not pdict[myusername]["impostor"] and not has:
              rtext(fnt(30), "Press SPACE to do task", actualheight - 98)
            if pdict[myusername]["impostor"] and globalminname and not pdict[myusername]["ghost"]:
              rtext(fnt(30), f"Press Q to beam {globalminname['nickname']}", [actualheight - 104, actualheight - 64][has])

            if doing_task:
              screen.blit(prime, (0,0))
              await globals()[functions[task]](relevant_entries, screen, actualwidth, actualheight)
            
            if (time.time() - base) < 0.035:
                await asyncio.sleep(0.035 - (time.time() - base))
            
            pg.display.flip()

        jsondata = await websocket.recv()
        if "[" not in jsondata:
          print(jsondata)
        data = json.loads(jsondata)
        handle_after = False
        for entry in data:
          if entry[0] == "Map":
            handle_after = True
          elif entry[0] == "Owner":
            is_owner = True
          elif entry[0] == "Meeting":
            globalitems = []
            meettype = entry[1]
            whodidit = entry[2]
            starttime = entry[3]
            endtime = entry[4] + starttime
            meeting_called = 3
            if entry[1] == 1:
              rtext(font5, "TOWN", actualheight//2 - 105, color = (255, 0, 0))
              rtext(font5, "HALL", actualheight//2 + 5, color = (255, 0, 0))
            elif entry[1] == 2:
              rtext(font5, "BURNOUT", actualheight//2 - 105, color = (255, 0, 0))
              rtext(font5, "REPORTED", actualheight//2 + 5, color = (255, 0, 0))
              e = entry[5]
              pscale(pg.transform.scale(oof, (150, 100)), actualwidth//2 - 75, actualheight//2 + 105, (e["h"], e["s"], e["l"]))
            pg.display.flip()
            delay(2.5)
            screen.fill((255, 255, 255))
            rightborder = 2*actualwidth//3
            playerstoadd = list(pdict.keys())
            i = 0
            for x in range(5):
              for pos in range(20):
                if i < len(playerstoadd) and playerstoadd[i] == whodidit:
                  col = (252, 186, 3)
                else: col = (200, 200, 200)
                if i < len(playerstoadd) and pdict[playerstoadd[i]]["ghost"]: col = (255, 0, 0)
                pg.draw.rect(screen, col, pg.Rect(x*rightborder//5 + 10, pos*37 + 10, rightborder//5 - 3, 33))
                if col == (252, 186, 3):
                  screen.blit(pg.font.Font("OpenSansEmoji.ttf", 10).render("(Called)", True, (0,0,0)), (x*rightborder//5 + 34, pos*37 + 28))
                if i < len(playerstoadd):
                  e = pdict[playerstoadd[i]]
                  pscale(pg.transform.scale(player, (20, 30)), x*rightborder//5 + 11, pos*37 + 11, (e["h"], e["s"], e["l"]), transp = e["ghost"])
                  screen.blit(pg.font.Font("OpenSansEmoji.ttf", 15).render(e["nickname"], True, (0,0,0)), (x*rightborder//5 + 34, pos*37 + 12))
                  i+= 1
                elif i == len(playerstoadd):
                  screen.blit(pg.font.Font("OpenSansEmoji.ttf", 15).render("Skip Vote", True, (0,0,0)), (x*rightborder//5 +  12, pos*37 + 12))
                  i += 1
            rtext(font2, "Discuss: who is it?", actualheight - 35, 2, color = (128, 128, 128))
            pr = f"Time Remaining: {round(endtime - time.time())}s"
            screen.blit(fnt(20).render(pr, True, (255, 0, 0)), (actualwidth//2 - fnt(20).size(pr)[0]//2, actualheight-35))
            screen.blit(font3.render("Press enter to send message.", True, (128, 128, 128)), (actualwidth - font3.size("Press enter to send message.")[0], actualheight-35))
            textbox(height - 70, 2*width//3 + 30, wdth = 440, col = (114, 247, 247), text = "", myfont = fnt(15))
            pg.display.flip()
          elif entry[0] == "Chat" and meeting_called == 3:
            storage.insert(0, entry[1])
            pg.draw.rect(screen, (255, 255, 255), pg.Rect(2*width//3 + 30, 0, width//3, height - 72))
            basey = 0
            for ent in storage:
              e = pdict[ent[0]]
              if e["ghost"] and not pdict[myusername]["ghost"]: continue
              message = ent[1]
              if ent[0] != myusername:
                pscale(pg.transform.scale(player, (40, 60)), width - 50, actualheight-35 - 100 - basey, (e["h"], e["s"], e["l"]), transp = e["ghost"])
                screen.blit(fnt(20).render(e["nickname"], True, (0,0,0)), (width - 60 - fnt(20).size(e["nickname"])[0], actualheight-35 - 100 - basey))
                screen.blit(fnt(15).render(message, True, (0,0,0)), (width - 60 - fnt(15).size(message)[0], actualheight-35 - 68 - basey))
              else:
                pscale(pg.transform.scale(player, (40, 60)), 2*width//3 + 30, actualheight-35 - 100 - basey, (e["h"], e["s"], e["l"]), transp = e["ghost"])
                screen.blit(fnt(20).render(e["nickname"], True, (0,0,0)), (2*width//3 + 80, actualheight-35 - 100 - basey))
                screen.blit(fnt(15).render(message, True, (0,0,0)), (2*width//3 + 80, actualheight-35 - 68 - basey))
              basey += 64
              if actualheight - 35 - 100 - basey <= 0: break
            pg.display.flip()

          elif entry[0] == "Task":
            task = entry[1]
          elif entry[0] == "Vote":
            voted[entry[1]] = entry[2]
            if len(voted) == len(pdict):
              kick_player = True
            flg = True
          elif entry[0] == "Beamed":
            pass # do some animation
          elif entry[0] == "Item":
            globalitems.append(entry[1])
          elif entry[0] == "Players":
            if not flag:
              flag = True
            for opt in entry[1]:
              if opt not in pdict: 
                pdict[opt] = entry[1][opt]
                pdict[opt]["f"] = 0
                pdict[opt]["f2"] = 0
              else:
                originalx = pdict[opt]["x"]
                originaly = pdict[opt]["y"]
                pdict[opt]["f"] = pdict[opt]["x"] < entry[1][opt]["x"]
                for field in entry[1][opt]:
                  pdict[opt][field] = entry[1][opt][field]
                if originalx != pdict[opt]["x"] or originaly != pdict[opt]["y"]:
                  pdict[opt]["f2"] = (pdict[opt]["f2"] + 1) % 2
                  if pdict[opt]["f2"] % 2 == 1:
                    whichleg = not whichleg
          elif entry[0] == "Left":
            del pdict[entry[1]]
            flag = True
            print(f"{entry[1]} left the game.")
        return_pressed = False
        if handle_after:
          return [[], is_owner]
        
        base = time.time()

      if flag and meeting_called != 3:
        offsetx = (pdict[myusername]["x"]*MS - width//2)
        offsety = (pdict[myusername]["y"]*MS - height//2)

        ox = (pdict[myusername]["x"] - width//2)
        oy = (pdict[myusername]["y"] - height//2)

        screen.fill((0,0,0))
        temp = pg.Surface((width, height))
        temp.blit(mainmap, (0,0), pg.Rect(ox, oy, width, height))
        temp = pg.transform.scale(temp, (width*MS, height*MS))
        screen.blit(temp, (0,0), pg.Rect(width, height, width, height))

        if task not in completed and (not pdict[myusername]["ghost"] or task != 1) and (not pdict[myusername]["impostor"] or task == 1):
          overmap = tasks[task]
          temp = pg.Surface((width, height), pg.SRCALPHA)
          temp.blit(overmap, (0,0), pg.Rect(ox, oy, width, height))
          temp = pg.transform.scale(temp, (width*MS, height*MS))
          screen.blit(temp, (0,0), pg.Rect(width, height, width, height))

        for e in globalitems:
          pscale(oof, e["x"]*MS-oof.get_width()//2 - offsetx, e["y"]*MS-oof.get_width()//2 - offsety, (e["h"], e["s"], e["l"]))

        for opt in pdict:
          e = pdict[opt]
          if e["x"]*MS in range(offsetx, offsetx + width) and e["y"]*MS in range(offsety, offsety + height) and (pdict[myusername]["ghost"] or not e["ghost"]):
            if e["f2"] > 0:
              todo = 1+whichleg
            else: todo = 0
            result = [[reverseplayer, player], [reversepwalking, pwalking], [reversepwalkingb, pwalkingb]][todo][e["f"]]
            pscale(result, e["x"]*MS-pwidth2//2 - offsetx, e["y"]*MS-pheight2//2 - offsety, (e["h"], e["s"], e["l"]), transp = e["ghost"])
            my = nmap(e["y"]*MS-50-pheight2//2 - offsety, 0, actualheight, 0, height)
            mx = nmap(e["x"]*MS - offsetx, 0, actualwidth, 0, width)
            rtext(thefont, pdict[opt]["nickname"], int(round(my)), int(round(mx)), color = (128,128,128), ctr = True)

        tasknames = pdict[myusername]["tasks"]
        total = len(tasknames) * len([p for p in pdict if not pdict[p]["impostor"]])
        complete = sum([sum([1 for t in pdict[u]["tasks"] if pdict[u]["tasks"][t]]) for u in pdict if not pdict[u]["impostor"]])

        by = 42
        results = {}
        try: ltext = f"TODO ({round(complete*100/total)}% total)"
        except: ltext = "TODO (100% total)"
        maxwidth = font4.size(ltext)[0] + 4
        if not pdict[myusername]["impostor"]:
          for tsk in tasknames:
            result = taskdesc[int(tsk)]
            if tasknames[tsk]: result += " (Complete)"
            results[tsk] = result
            if font3.size(result)[0] + 4 > maxwidth:
              maxwidth = font3.size(result)[0] + 4

          tasklist = pg.Surface((maxwidth, len(tasknames)*25 + 40), pg.SRCALPHA)
          tasklist.fill((255, 255, 255, 220))
          screen.blit(tasklist, (2, 2))
          screen.blit(font4.render(ltext, True, (0,0,0)), (2, 2))
          for tsk in tasknames:
            screen.blit(font3.render(results[tsk], True, [(215, 146, 146), (136, 255, 136)][tasknames[tsk]]), (2, by))
            by += 25

        else:
          tasklist = pg.Surface((maxwidth, 2*25 + 40), pg.SRCALPHA)
          tasklist.fill((255, 255, 255, 220))
          screen.blit(tasklist, (2, 2))
          screen.blit(font4.render(ltext, True, (0,0,0)), (2, 2))
          screen.blit(font3.render("Ruin everyone as BRC.", True, (215, 146, 146)), (2, by))
          by += 25
          diff = max(0, round(pdict[myusername]["killcooldown"] + globalkcool - time.time()))
          if diff == 0: phr = "You can beam now."
          else: phr = f"You can beam again in {diff}s."
          screen.blit(font3.render(phr, True, (215, 146, 146)), (2, by))

        minimum = math.inf
        minname = None
        if pdict[myusername]["impostor"] and round(pdict[myusername]["killcooldown"] + globalkcool - time.time()) <= 0:
          a = pdict[myusername]
          for opt in pdict:
            if opt == myusername or pdict[opt]["ghost"]: continue
            b = pdict[opt]
            dist = (a["x"] - b["x"])**2 + (a["y"] - b["y"])**2
            if dist < a["krange"]**2 and dist < minimum:
              minimum = dist
              minname = b

        minrep = math.inf
        namerep = None
        if not pdict[myusername]["ghost"]:
          a = pdict[myusername]
          for b in globalitems:
            dist = (a["x"] - b["x"])**2 + (a["y"] - b["y"])**2
            if dist < 48**2 and dist < minrep:
              minrep = dist
              namerep = b

        globalminname = minname
        globalminrep = namerep

        pg.draw.rect(screen, (128, 128, 128), pg.Rect(actualwidth//2 - 300, actualheight - 100, 600, 70))
        has = False
        if globalminrep and not pdict[myusername]["ghost"]:
          has = True
          rtext(fnt(30), "Press R to report", actualheight - 98)
        if task == 1 and not pdict[myusername]["ghost"] and not has:
          rtext(fnt(30), "Press SPACE to call meeting", actualheight - 98)
          has = True
        elif task not in [0, 1, 255] and not pdict[myusername]["impostor"] and not has:
          rtext(fnt(30), "Press SPACE to do task", actualheight - 98)
        if pdict[myusername]["impostor"] and globalminname and not pdict[myusername]["ghost"]:
          rtext(fnt(30), f"Press Q to beam {minname['nickname']}", [actualheight - 104, actualheight - 64][has])

        if doing_task:
          screen.blit(prime, (0,0))
          await globals()[functions[task]](relevant_entries, screen, actualwidth, actualheight)

        if (time.time() - base) < 0.07:
            await asyncio.sleep((0.07) - (time.time() - base))
        pg.display.flip()

      if kick_player:
        pg.mouse.set_cursor(*pg.cursors.arrow)
        screen.fill((255, 255, 255))
        rightborder = 2*actualwidth//3
        playerstoadd = list(pdict.keys())
        i = 0
        for x in range(5):
          for pos in range(20):
            call = False
            col = [200, 200, 200]
            if i < len(playerstoadd) and playerstoadd[i] == whodidit:
              col = [252, 186, 3]
              call = True
            if myusername in voted:
              if i < len(playerstoadd) and voted[myusername] == playerstoadd[i]:
                if voted[myusername] == whodidit:
                  col = [226, 235, 52]
                else: col = [97, 235, 52]
              elif i == len(playerstoadd) and voted[myusername] == "skip":
                col = [97, 235, 52]
            if i < len(playerstoadd) and pdict[playerstoadd[i]]["ghost"]: col = [255, 0, 0]
            pg.draw.rect(screen, col, pg.Rect(x*rightborder//5 + 10, pos*37 + 10, rightborder//5 - 3, 33))
            extra = ""
            if call:
              extra += "(Called) "
            if i <= len(playerstoadd):
              numvotes = list(voted.values()).count((playerstoadd+["skip"])[i])
              if i == len(playerstoadd):
                numvotes += len(playerstoadd) - len(voted)
              extra += f"{numvotes} {['votes', 'vote'][numvotes == 1]}"
            if extra:
              screen.blit(pg.font.Font("OpenSansEmoji.ttf", 10).render(extra, True, (0,0,0)), (x*rightborder//5 + 34, pos*37 + 28))
            if i < len(playerstoadd):
              e = pdict[playerstoadd[i]]
              pscale(pg.transform.scale(player, (20, 30)), x*rightborder//5 + 11, pos*37 + 11, (e["h"], e["s"], e["l"]), transp = e["ghost"])
              screen.blit(pg.font.Font("OpenSansEmoji.ttf", 15).render(e["nickname"], True, (0,0,0)), (x*rightborder//5 + 34, pos*37 + 12))
              i+= 1
            elif i == len(playerstoadd):
              screen.blit(pg.font.Font("OpenSansEmoji.ttf", 15).render("Skip Vote", True, (0,0,0)), (x*rightborder//5 +  12, pos*37 + 12))
              i += 1
        pg.display.flip()
        delay(2)
        fade()
        delay(0.5)
        votecounts = {}
        for playerx in voted:
          if voted[playerx] not in votecounts:
            votecounts[voted[playerx]] = 0
          else:
            votecounts[voted[playerx]] += 1
        maxnum = max(list(votecounts.values()))
        highest = []
        for playerx in votecounts:
          if votecounts[playerx] == maxnum:
            highest.append(playerx)
        if len(highest) == 1:
          if highest[0] == "skip":
            phrase = "Nobody was expelled (skipped)."
          else:
            pdict[highest[0]]["ghost"] = 1
            if pdict[highest[0]]["impostor"]:
              phrase = f"{pdict[highest[0]]['nickname']} was a BRC."
            else: phrase = f"{pdict[highest[0]]['nickname']} was not a BRC."
        else:
          phrase = "Nobody was expelled (tie)."
        fsize = 100
        while fnt(fsize).size(phrase)[0] > width:
          fsize -= 2
        rtext(fnt(fsize), phrase, actualheight//2)
        numbrc = len([b for b in pdict if not pdict[b]["ghost"] and pdict[b]["impostor"]])
        rtext(fnt(70), f"{numbrc} BRC remain{['s', ''][numbrc != 1]}", actualheight//2 + 130)
        pg.display.flip()
        delay(2)
        kick_player = False
        meeting_called = 0
        textinput = ""
        flg = False
        return_pressed = False
        playerstoadd = None
        storage = []
        curnum = -1
        whodidit = None
        should_vote = False
        kick_player = False
        endtime = 0
        voted = {}
        bipflag = True

    if not bipflag:
      flag = False
    else:
      flag = True
    bipflag = False
      

async def lobby(websocket, data, is_owner):
  global screen, size, width, height, myusername, actualwidth, actualheight
  radius = int(math.ceil(math.sqrt((width//2)**2 + (height//2)**2)))
  if "[" not in data:
    print(data)
    await websocket.send("leave")
    await websocket.recv()
    return
  data = json.loads(data)
  for i in range(len(data)):
    if data[i][0] == "Owner":
      is_owner = True
      del data[i]
      break
  game = data[0][1]
  players = data[1][1]
  blounge = load("lounge_temp.png", width, height)
  for i in range(radius, 0, -10):
    screen.blit(blounge, (0, 0))
    pg.draw.circle(screen, (0,0,0), (width//2, height//2), radius, i)
    pg.display.flip()

  player = load("player.png", pwidth, pheight)
  reverseplayer = pg.transform.flip(player, True, False)
  pwalking = load("playerwalkingfront.png", pwidth, pheight)
  reversepwalking = pg.transform.flip(pwalking, True, False)
  pwalkingb = load("playerwalkingback.png", pwidth, pheight)
  reversepwalkingb = pg.transform.flip(pwalkingb, True, False)

  pdict = {}
  fsize = nmap(40, 0, actualwidth, 0, width)
  thefont = pg.font.Font("OpenSansEmoji.ttf", int(round(fsize)))
  for entry in players:
    pdict[entry] = players[entry]
    pdict[entry]["ghost"] = 0
    e = pdict[entry]
    e["f"] = 0
    e["f2"] = 0
    pscale(player, e["x"]-pwidth//2, e["y"]-pheight//2, (e["h"], e["s"], e["l"]), transp = e["ghost"])
    my = nmap(e["y"]-50-pheight//2, 0, actualheight, 0, height)
    mx = nmap(e["x"], 0, actualwidth, 0, width)
    rtext(thefont, pdict[entry]["nickname"], int(round(my)), int(round(mx)), color = (128,128,128), ctr = True)
  pg.display.flip()
  whichleg = True
  while True:
    flag = False
    keys = pg.key.get_pressed()
    spacestate = 0
    for event in pg.event.get():
      if event.type == QUIT: 
        sys.exit()
      elif event.type == VIDEORESIZE:
        size = width, height = (event.w, event.h)
        screen = pg.display.set_mode(size, pg.RESIZABLE)
        blounge = load("lounge_temp.png", width, height)
        flag = True
        pg.display.flip()
      elif event.type == KEYDOWN and event.key == K_SPACE:
        spacestate = 1
    if keys[K_RETURN] and is_owner:
      result = await play(websocket, pdict, is_owner)
      for entry in json.loads(result[0]):
        if entry[0] == "Players":
          if not flag:
            flag = True
          for opt in entry[1]:
            if opt not in pdict: 
              pdict[opt] = entry[1][opt]
              pdict[opt]["f"] = 0
              pdict[opt]["f2"] = 0
            else:
              originalx = pdict[opt]["x"]
              originaly = pdict[opt]["y"]
              pdict[opt]["f"] = pdict[opt]["x"] < entry[1][opt]["x"]
              for field in entry[1][opt]:
                pdict[opt][field] = entry[1][opt][field]
              if originalx != pdict[opt]["x"] or originaly != pdict[opt]["y"]:
                pdict[opt]["f2"] = (pdict[opt]["f2"] + 1) % 2
                if pdict[opt]["f2"] % 2 == 1:
                  whichleg = not whichleg
            pdict[opt]["ghost"] = 0
        elif entry[0] == "Left":
          del pdict[entry[1]]
          flag = True
          print(f"{entry[1]} left the game.")

    if keys[K_ESCAPE]:
      await websocket.send("leave")
      await websocket.recv()
      break
    await websocket.send(f"move,{keys[K_DOWN]},{keys[K_UP]},{keys[K_LEFT]},{keys[K_RIGHT]},{spacestate}")
    jsondata = await websocket.recv()
    if "[" not in jsondata:
      print(jsondata)
    data = json.loads(jsondata)
    handle_after = False
    for entry in data:
      if entry[0] == "Owner":
        is_owner = True
      elif entry[0] == "Map":
        handle_after = True
        
      elif entry[0] == "Players":
        if not flag:
          flag = True
        for opt in entry[1]:
          if opt not in pdict: 
            pdict[opt] = entry[1][opt]
            pdict[opt]["f"] = 0
            pdict[opt]["f2"] = 0
          else:
            originalx = pdict[opt]["x"]
            originaly = pdict[opt]["y"]
            pdict[opt]["f"] = pdict[opt]["x"] < entry[1][opt]["x"]
            for field in entry[1][opt]:
              pdict[opt][field] = entry[1][opt][field]
            if originalx != pdict[opt]["x"] or originaly != pdict[opt]["y"]:
              pdict[opt]["f2"] = (pdict[opt]["f2"] + 1) % 2
              if pdict[opt]["f2"] % 2 == 1:
                whichleg = not whichleg
          pdict[opt]["ghost"] = 0
      elif entry[0] == "Left":
        del pdict[entry[1]]
        flag = True
        print(f"{entry[1]} left the game.")
    if handle_after:
      result = await play(websocket, pdict, is_owner)
      is_owner = result[1]
      for entry in json.loads(result[0]):
        if entry[0] == "Owner":
          is_owner = True
        elif entry[0] == "Players":
          if not flag:
            flag = True
          for opt in entry[1]:
            if opt not in pdict: 
              pdict[opt] = entry[1][opt]
              pdict[opt]["f"] = 0
              pdict[opt]["f2"] = 0
            else:
              originalx = pdict[opt]["x"]
              originaly = pdict[opt]["y"]
              pdict[opt]["f"] = pdict[opt]["x"] < entry[1][opt]["x"]
              for field in entry[1][opt]:
                pdict[opt][field] = entry[1][opt][field]
              if originalx != pdict[opt]["x"] or originaly != pdict[opt]["y"]:
                pdict[opt]["f2"] = (pdict[opt]["f2"] + 1) % 2
                if pdict[opt]["f2"] % 2 == 1:
                  whichleg = not whichleg
            pdict[opt]["ghost"] = 0
        elif entry[0] == "Left":
          del pdict[entry[1]]
          flag = True
          print(f"{entry[1]} left the game.")

    if flag:
      screen.blit(blounge, (0, 0))
      for opt in pdict:
        e = pdict[opt]
        if e["f2"] == 1:
          todo = 1+whichleg
        else:
          todo = 0

        result = [[reverseplayer, player], [reversepwalking, pwalking], [reversepwalkingb, pwalkingb]][todo][e["f"]]
        pscale(result, e["x"]-pwidth//2, e["y"]-pheight//2, (e["h"], e["s"], e["l"]), transp = e["ghost"])
        my = nmap(e["y"]-50-pheight//2, 0, actualheight, 0, height)
        mx = nmap(e["x"], 0, actualwidth, 0, width)
        rtext(thefont, pdict[opt]["nickname"], int(round(my)), int(round(mx)), color = (128,128,128), ctr = True)
      pg.display.flip()
    await asyncio.sleep(0.07)

async def customize(websocket, appearance):
  global size, width, height, saved
  player = load("player.png", pwidth*2, pheight*2)
  pg.mouse.set_cursor(*pg.cursors.arrow)
  display_menu()
  [appearance["h"], appearance["s"], appearance["l"]]
  lx = appearance["l"]
  flip = True
  mx = int(round(2*appearance["s"]*math.cos(appearance["h"]*math.pi/180)+ width//2))
  my = int(round(2*appearance["s"]*math.sin(appearance["h"]*math.pi/180)+ height//2))
  plate = saved[lx].copy()
  col = plate.get_at((mx-width//2+200, my-height//2+200))
  for changex in range (-2, 3):
    for changey in range(-2, 3):
      coord = [mx-width//2+200+changex, my-height//2+200+changey]
      try:
        if plate.get_at(coord) != (0,0,0,0):
          plate.fill((255, 255, 255), (coord, (1,1)))
      except IndexError: pass
  screen.blit(plate, (width//2 - 200, height//2 - 200))
  del plate
  textbox(height-80, width//2 - 280, text = f"R: {col[0]}, G: {col[1]}, B: {col[2]}")
  textbox(height-80, width//2 + 20, text = f"H: {int(round(col.hsla[0]))}, S: {int(round(col.hsla[1]))}%, L: {int(round(col.hsla[2]))}%")
  textbox(height//3 - 100, 3*width//4, col = (114, 247, 247), text = appearance['nickname'])
  pscale(player, 3*width//4, height//3, col, True)
  screen.blit(save, (width - 252, 2))
  screen.blit(cancel, (width- 512, 2))
  pg.display.flip()
  dragging = False
  nickname = appearance['nickname']
  hsquare = -1

  while True:
    for event in pg.event.get():
      if event.type == QUIT: 
        sys.exit()
      elif event.type == MOUSEBUTTONUP:
        dragging = False
        if event.button in [4, 5]:
          if event.button == 4: 
            if lx == 0: continue
          else: 
            if lx == 100: continue
          lx += [-1, 1][event.button == 5]
          plate = saved[lx].copy()
          col = plate.get_at((mx-width//2+200, my-height//2+200))
          for changex in range (-2, 3):
            for changey in range(-2, 3):
              coord = [mx-width//2+200+changex, my-height//2+200+changey]
              try:
                if plate.get_at(coord) != (0,0,0,0):
                  plate.fill((255, 255, 255), (coord, (1,1)))
              except IndexError: pass
          screen.blit(plate, (width//2 - 200, height//2 - 200))
          del plate
          textbox(height-80, width//2 - 280, text = f"R: {col[0]}, G: {col[1]}, B: {col[2]}")
          textbox(height-80, width//2 + 20, text = f"H: {int(round(col.hsla[0]))}, S: {int(round(col.hsla[1]))}%, L: {int(round(col.hsla[2]))}%")
          pscale(player, 3*width//4, height//3, col, True)
          pg.display.flip()
        if hsquare == 1:
          return None

        elif hsquare == 0:
          plate = saved[lx].copy()
          col = plate.get_at((mx-width//2+200, my-height//2+200))
          await websocket.send(f"appear,{nickname},{int(round(col.hsla[0]))},{int(round(col.hsla[1]))},{int(round(col.hsla[2]))},{appearance['hat']},{appearance['suit']},{appearance['pet']},{appearance['faculty']}")
          res = await websocket.recv()
          if "[" not in res:
            flip = 1 - flip
            textbox(3*height//4 +77, x = 4, text = res, wdth = width-8, col = [(255, 255, 255), (255, 0, 0)][flip], textcol = (255, 0, 0))
            pg.display.flip()
          else:
            return [nickname, int(round(col.hsla[0])), int(round(col.hsla[1])), int(round(col.hsla[2]))]
      elif event.type == MOUSEBUTTONDOWN:
        dragging = True
      elif event.type == KEYDOWN:
        if event.key == K_BACKSPACE:
          nickname = nickname[:-1]
          textbox(height//3 - 100, 3*width//4, col = (114, 247, 247), text = nickname)
          pg.display.flip()
        elif event.unicode not in ",{}[]|\\":
          keys = pg.key.get_pressed()
          if keys[K_RSHIFT] or keys[K_LSHIFT]:
            nickname += event.unicode.upper()
          else:
            nickname += event.unicode
          if font3.size(nickname)[0] > 258 or len(nickname) > 32:
            nickname = nickname[:-1]
          textbox(height//3 - 100, 3*width//4, col = (114, 247, 247), text = nickname)
          pg.display.flip()
    tx, ty = pg.mouse.get_pos()
    if intercept(tx, ty, width-252, 2, 250, 71):
      if hsquare != 0:
        hsquare = 0
        pg.mouse.set_cursor(*pg.cursors.diamond)
        screen.blit(save2, (width - 252, 2))
        screen.blit(cancel, (width- 512, 2))
        pg.display.flip()

    elif intercept(tx, ty, width-512, 2, 250, 71):
      if hsquare != 1:
        hsquare = 1
        pg.mouse.set_cursor(*pg.cursors.diamond)
        screen.blit(save, (width - 252, 2))
        screen.blit(cancel2, (width- 512, 2))
        pg.display.flip()

    elif hsquare != -1:
      hsquare = -1
      screen.blit(save, (width - 252, 2))
      screen.blit(cancel, (width- 512, 2))
      pg.mouse.set_cursor(*pg.cursors.arrow)
      pg.display.flip()

    if dragging and (tx-width//2)**2 + (ty - height//2)**2 <= 40000:
      mx, my = tx, ty
      plate = saved[lx].copy()
      col = plate.get_at((mx-width//2+200, my-height//2+200))
      for changex in range (-2, 3):
        for changey in range(-2, 3):
          coord = [mx-width//2+200+changex, my-height//2+200+changey]
          try:
            if plate.get_at(coord) != (0,0,0,0):
              plate.fill((255, 255, 255), (coord, (1,1)))
          except IndexError: pass
      screen.blit(plate, (width//2 - 200, height//2 - 200))
      del plate
      textbox(height-80, width//2 - 280, text = f"R: {col[0]}, G: {col[1]}, B: {col[2]}")
      textbox(height-80, width//2 + 20, text = f"H: {int(round(col.hsla[0]))}, S: {int(round(col.hsla[1]))}%, L: {int(round(col.hsla[2]))}%")
      pscale(player, 3*width//4, height//3, col, True)
      pg.display.flip()

    await asyncio.sleep(0.03)

async def create_game(websocket, data):
  global size, width, height
  pg.mouse.set_cursor(*pg.cursors.arrow)
  display_menu()
  rtext(font2, "Name: ", height//4, width//2-font2.size("Name: ")[0]//2)
  rtext(font2, "Map: UBC (cannot change yet)", height//4 + 35, 5)
  rtext(font2, "Mode: Normal (cannot change yet)", height//4 + 70, 5)
  rtext(font2, "Type: Public (cannot change yet)", height//4 + 105, 5)

  textbox(2*height//8+5, 3*width//5, col = (114, 247, 247), text = "Name Your Game", textcol = (0, 200, 200))
  inputs = ""

  screen.blit(start, (width//2+10, 3*height//4))
  screen.blit(cancel, (width//2-261, 3*height//4))

  pg.display.flip()
  cur = 0
  hsquare = -1
  flip = False
  while True:
    x, y = pg.mouse.get_pos()
    if x in range(3*width//5, 3*width//5+260):
      if y in range(2*height//8-3, 2*height//8+37):
        if hsquare != -2:
          hsquare = -2
          pg.mouse.set_cursor(*pg.cursors.diamond)

      elif hsquare == -2:
        hsquare = -1
        screen.blit(start, (width//2+10, 3*height//4))
        screen.blit(cancel, (width//2-261, 3*height//4))
        pg.mouse.set_cursor(*pg.cursors.arrow)
        pg.display.flip()

    if intercept(x, y, width//2 - 261, 3*height//4, 251, 71):
      if hsquare != 0:
        hsquare = 0
        pg.mouse.set_cursor(*pg.cursors.diamond)
        screen.blit(start, (width//2 + 10, 3*height//4))
        screen.blit(cancel2, (width//2-261, 3*height//4))
        pg.display.flip()

    elif intercept(x, y, width//2 + 10, 3*height//4, 251, 71):
      if hsquare != 1:
        hsquare = 1
        pg.mouse.set_cursor(*pg.cursors.diamond)
        screen.blit(start2, (width//2 + 10, 3*height//4))
        screen.blit(cancel, (width//2-261, 3*height//4))
        pg.display.flip()

    elif hsquare != -1:
      hsquare = -1
      screen.blit(start, (width//2+10, 3*height//4))
      screen.blit(cancel, (width//2-261, 3*height//4))
      pg.mouse.set_cursor(*pg.cursors.arrow)
      pg.display.flip()

    for event in pg.event.get():
      if event.type == QUIT: 
        sys.exit()
      elif event.type == MOUSEBUTTONUP:
        if hsquare == 0:
          return

        elif hsquare == 1:
          await websocket.send(f"make,{inputs},1,0,0")
          res = await websocket.recv()
          if "[" not in res:
            flip = 1 - flip
            textbox(3*height//4 +77, x = 4, text = res, wdth = width-8, col = [(255, 255, 255), (255, 0, 0)][flip], textcol = (255, 0, 0))
            pg.display.flip()
          else:
            pg.mouse.set_cursor(*pg.cursors.arrow)
            radius = int(math.ceil(math.sqrt((width//2)**2 + (height//2)**2)))
            for i in range(radius, 0, -1):
              pg.draw.circle(screen, (0,0,0), (width//2, height//2), i, 1)
              pg.display.flip()
            await lobby(websocket, res, True)
            return
            
      elif event.type == KEYDOWN:
        if event.key == K_BACKSPACE:
          inputs = inputs[:-1]
          if inputs == "":
            textbox((cur+2)*height//8+5, 3*width//5, col = (114, 247, 247), text = "Name your Game", textcol = (0, 200, 200))
          else: 
            textbox((cur+2)*height//8+5, 3*width//5, col = (114, 247, 247), text = inputs)
          pg.display.flip()
        elif event.unicode not in ",{}[]|\\":
          keys = pg.key.get_pressed()
          if keys[K_RSHIFT] or keys[K_LSHIFT]:
            inputs += event.unicode.upper()
          else:
            inputs += event.unicode
          if font3.size(inputs)[0] > 258 or len(inputs) > 32:
            inputs = inputs[:-1]
          if inputs == "":
            textbox((cur+2)*height//8+5, 3*width//5, col = (114, 247, 247), text = "Name your Game", textcol = (0, 200, 200))
          else: 
            textbox((cur+2)*height//8 +5, 3*width//5, col = (114, 247, 247), text = inputs)
          pg.display.flip()

    await asyncio.sleep(0.03)

async def prompt(websocket, confirm):
  global screen, size, width, height, myusername
  pg.mouse.set_cursor(*pg.cursors.arrow)
  
  hsquare = -1
  inputs = ["", "", ""]
  cur = 0
  display_menu()
  if confirm:
    go = create
    go2 = create2
  else:
    go = login
    go2 = login2

  screen.blit(go, (width//2+10, 3*height//4))
  screen.blit(cancel, (width//2-261, 3*height//4))
  playermap = pg.Surface((562, height//2), pg.SRCALPHA)
  playermap.fill((255,255,255,75))  
  screen.blit(playermap, (width//2-281, height//4))

  if confirm: thetext = "Create an Account"
  else: thetext = "Login to your Account"
  rtext(pg.font.Font("OpenSansEmoji.ttf", 40), thetext, height//4 + 5, color = (0, 128, 128))

  phrase = "Username: "
  wdth = font2.size(phrase)[0]
  rtext(font2, phrase, 3*height//8, width//2-wdth)
  textbox(3*height//8, col = (114, 247, 247))

  phrase = "Password: "
  wdth = font2.size(phrase)[0]
  rtext(font2, phrase, height//2, width//2-wdth)
  textbox(height//2)

  rtext(font2, "Click protected boxes to show hidden text.", 105)

  if confirm:
    phrase = "Confirm Password: "
    wdth = font2.size(phrase)[0]
    rtext(font2, phrase, 5*height//8, width//2-wdth)
    textbox(5*height//8)
  flip = True
  pg.display.flip()
  while True:
    x, y = pg.mouse.get_pos()
    if x in range(width//2, width//2+260):
      if y in range(3*height//8-3, 3*height//8+37):
        if hsquare != 0:
          hsquare = 0
          pg.mouse.set_cursor(*pg.cursors.diamond)
    
      elif y in range(4*height//8-3, 4*height//8+37):
        if hsquare != 1:
          hsquare = 1
          pg.mouse.set_cursor(*pg.cursors.diamond)

      elif confirm and y in range(5*height//8-3, 5*height//8+37):
        if hsquare != 2:
          hsquare = 2
          pg.mouse.set_cursor(*pg.cursors.diamond)

      elif hsquare in range(2+confirm):
        hsquare = -1
        screen.blit(cancel, (width//2-261, 3*height//4))
        screen.blit(go, (width//2+10, 3*height//4))
        pg.mouse.set_cursor(*pg.cursors.arrow)
        pg.display.flip()

    if x in range(width//2-261, width//2-10) and y in range(3*height//4, 3*height//4+71):
      if hsquare != 3:
        hsquare = 3
        pg.mouse.set_cursor(*pg.cursors.diamond)
        screen.blit(cancel2, (width//2-261, 3*height//4))
        screen.blit(go, (width//2+10, 3*height//4))
        pg.display.flip()

    elif x in range(width//2+10, width//2+261) and y in range(3*height//4, 3*height//4+71):
      if hsquare != 4:
        hsquare = 4
        pg.mouse.set_cursor(*pg.cursors.diamond)
        screen.blit(go2, (width//2+10, 3*height//4))
        screen.blit(cancel, (width//2-261, 3*height//4))
        pg.display.flip()

    elif hsquare in [3, 4]:
      hsquare = -1
      screen.blit(cancel, (width//2-261, 3*height//4))
      screen.blit(go, (width//2+10, 3*height//4))
      pg.mouse.set_cursor(*pg.cursors.arrow)
      pg.display.flip()
    flag = False
    for event in pg.event.get():
      if event.type == QUIT: 
        sys.exit()
      elif event.type == MOUSEBUTTONUP:
        if hsquare in range(2+confirm):
          if cur > 0:
            toprint = "*"*len(inputs[cur])
          else:
            toprint = inputs[cur]
          textbox((cur+3)*height//8, text = toprint)
          cur = hsquare
          textbox((cur+3)*height//8, col = (114, 247, 247), text = inputs[cur])
          pg.display.flip()
        elif hsquare == 3:
          display_menu()
          screen.blit(login, (width//2+10, height//4))
          screen.blit(signup, (width//2-261, height//4))
          pg.display.flip()
          pg.mouse.set_cursor(*pg.cursors.arrow)
          return None
        elif hsquare == 4 and (not confirm or inputs[1] == inputs[2]):
          await websocket.send(f"{['login','signup'][confirm]},{inputs[0]},{inputs[1]}")
          res = await websocket.recv()
          if "[" not in res:
            flip = 1 - flip
            textbox(3*height//4 +77, x = 4, text = res, wdth = width-8, col = [(255, 255, 255), (255, 0, 0)][flip], textcol = (255, 0, 0))
            pg.display.flip()
          else:
            myusername = inputs[0]
            pg.mouse.set_cursor(*pg.cursors.arrow)
            return [inputs] + json.loads(res)
      if event.type == KEYDOWN:
        if event.key in [K_RETURN, K_TAB]:
          if cur > 0:
            toprint = "*"*len(inputs[cur])
          else:
            toprint = inputs[cur]
          textbox((cur+3)*height//8, text = toprint)
          cur = (cur + 1) % (2+confirm)
          if cur > 0:
            toprint = "*"*len(inputs[cur])
          else:
            toprint = inputs[cur]
          col = (255, 255, 255)
          if confirm and cur == 2 and inputs[1] != inputs[2]:
            col = (255, 0, 0)
          textbox((cur+3)*height//8, col = (114, 247, 247), text = toprint, textcol = col)
          pg.display.flip()
        elif event.key == K_BACKSPACE:
          inputs[cur] = inputs[cur][:-1]
          if cur > 0:
            toprint = "*"*len(inputs[cur])
          else:
            toprint = inputs[cur]
          col = (255, 255, 255)
          if confirm and cur == 2 and inputs[1] != inputs[2]:
            col = (255, 0, 0)
          textbox((cur+3)*height//8, col = (114, 247, 247), text = toprint, textcol = col)
          pg.display.flip()
        elif event.unicode not in ",{}[]|":
          keys = pg.key.get_pressed()
          if keys[K_RSHIFT] or keys[K_LSHIFT]:
            inputs[cur] += event.unicode.upper()
          else:
            inputs[cur] += event.unicode
          if cur > 0:
            toprint = "*"*len(inputs[cur])
          else:
            toprint = inputs[cur]
          if font3.size(toprint)[0] > 258 or len(toprint) > 32:
            inputs[cur] = inputs[cur][:-1]
            toprint = toprint[:-1]
          col = (255, 255, 255)
          if confirm and cur == 2 and inputs[1] != inputs[2]:
            col = (255, 0, 0)
          textbox((cur+3)*height//8, col = (114, 247, 247), text = toprint, textcol = col)
          pg.display.flip()
    await asyncio.sleep(0.03)

async def delete_account(websocket):
  global screen, size, width, height
  display_menu()
  screen.blit(no, (width//2 + 10, height//2))
  screen.blit(yes, (width//2 - 209, height//2))
  rtext(font, "DELETE ACCOUNT?", height//4, color = (255, 0, 0))
  rtext(font2, "This action cannot be undone.", height//4 + 75, color = (255, 0, 0))
  pg.display.flip()

  hsquare = -1

  while True:
    x, y = pg.mouse.get_pos()
    if intercept(x, y, width//2+10, height//2, 199, 71):
      if hsquare != 0:
        hsquare = 0
        pg.mouse.set_cursor(*pg.cursors.diamond)
        screen.blit(no2, (width//2 + 10, height//2))
        screen.blit(yes, (width//2 - 209, height//2))
        pg.display.flip()

    elif intercept(x, y, width//2 - 209, height//2, 199, 71):
      if hsquare != 1:
        hsquare = 1
        pg.mouse.set_cursor(*pg.cursors.diamond)
        screen.blit(no, (width//2 + 10, height//2))
        screen.blit(yes2, (width//2 - 209, height//2))
        pg.display.flip()

    elif hsquare != -1:
      hsquare = -1
      screen.blit(no, (width//2 + 10, height//2))
      screen.blit(yes, (width//2 - 209, height//2))
      pg.mouse.set_cursor(*pg.cursors.arrow)
      pg.display.flip()

    for event in pg.event.get():
      if event.type == QUIT: 
        sys.exit()
      elif event.type == MOUSEBUTTONUP:
        if hsquare == 0:
          return True

        elif hsquare == 1:
          await websocket.send("delete")
          await websocket.recv()
          display_menu()
          screen.blit(login, (width//2+10, height//4))
          screen.blit(signup, (width//2-261, height//4))
          pg.display.flip()
          pg.mouse.set_cursor(*pg.cursors.arrow)
          return False

    await asyncio.sleep(0.03)

def mainmenuicons():
  global width, height
  screen.blit(game, (10, 2*height//8))
  screen.blit(private, (10, 3*height//8))
  screen.blit(public, (10, 4*height//8))
  screen.blit(logout, (10, 6*height//9))
  screen.blit(delete, (10, 7*height//9))
  screen.blit(shirt, (width-137, 30))

def intercept(x, y, x2, y2, w = 447, h = 47):
  return x in range(x2, x2+w) and y in range(y2, y2+h)

async def mainmenu(websocket, inputs):
  global screen, size, width, height
  display_menu()
  mainmenuicons()
  data = inputs[0]
  appearance = inputs[2][1]
  textbox(3*height//8+5, 3*width//5, col = (114, 247, 247), text = "Enter Code", textcol = (0, 200, 200))
  try: rtext(font2, f"Hi {appearance['nickname']} ({data[0]})", 105, color = (66, 245, 245))
  except: print(appearance)
  player = load("player.png", pwidth*2, pheight*2)
  pscale(player, 3*width//4, height//2, [appearance["h"], appearance["s"], appearance["l"]])
  #{'nickname': 'James', 'username': 'James', 'h': 189, 's': 100, 'l': 50, 'x': 590, 'y': 446, 'hat': 0, 'suit': 0, 'pet': 0, 'faculty': 0}
  pg.display.flip()

  cur = 1
  hsquare = -1
  inputs = ""
  flip = False
  while True:
    x, y = pg.mouse.get_pos()
    if x in range(3*width//5, 3*width//5+260):
      if y in range(3*height//8-3, 3*height//8+37):
        if hsquare != 1:
          hsquare = 1
          pg.mouse.set_cursor(*pg.cursors.diamond)

      elif hsquare == 1:
        hsquare = -1
        mainmenuicons()
        pg.mouse.set_cursor(*pg.cursors.arrow)
        pg.display.flip()

    if intercept(x, y, 10, 2*height//8):
      if hsquare != 2:
        hsquare = 2
        pg.mouse.set_cursor(*pg.cursors.diamond)
        mainmenuicons()
        screen.blit(game2, (10, 2*height//8))
        pg.display.flip()

    elif intercept(x, y, 10, 3*height//8):
      if hsquare != 3:
        hsquare = 3
        pg.mouse.set_cursor(*pg.cursors.diamond)
        mainmenuicons()
        screen.blit(private2, (10, 3*height//8))
        pg.display.flip()

    elif intercept(x, y, 10, 4*height//8):
      if hsquare != 4:
        hsquare = 4
        pg.mouse.set_cursor(*pg.cursors.diamond)
        mainmenuicons()
        screen.blit(public2, (10, 4*height//8))
        pg.display.flip()

    elif intercept(x, y, 10, 6*height//9):
      if hsquare != 5:
        hsquare = 5
        pg.mouse.set_cursor(*pg.cursors.diamond)
        mainmenuicons()
        screen.blit(logout2, (10, 6*height//9))
        pg.display.flip()

    elif intercept(x, y, 10, 7*height//9):
      if hsquare != 6:
        hsquare = 6
        pg.mouse.set_cursor(*pg.cursors.diamond)
        mainmenuicons()
        screen.blit(delete2, (10, 7*height//9))
        pg.display.flip()

    elif intercept(x, y, width-137, 30, 127, 71):
      if hsquare != 7:
        hsquare = 7
        pg.mouse.set_cursor(*pg.cursors.diamond)
        mainmenuicons()
        screen.blit(shirt2, (width-137, 30))
        pg.display.flip()

    elif hsquare != -1:
      hsquare = -1
      mainmenuicons()
      pg.mouse.set_cursor(*pg.cursors.arrow)
      pg.display.flip()

    for event in pg.event.get():
      if event.type == QUIT: 
        sys.exit()
      elif event.type == MOUSEBUTTONUP:
        if hsquare == 2:
          await create_game(websocket, data)
          return True

        elif hsquare == 3:
          await websocket.send(f"join,{inputs}")
          res = await websocket.recv()
          if "[" not in res:
            flip = 1 - flip
            textbox(3*height//4 +77, x = 4, text = res, wdth = width-8, col = [(255, 255, 255), (255, 0, 0)][flip], textcol = (255, 0, 0))
            pg.display.flip()
          else:
            pg.mouse.set_cursor(*pg.cursors.arrow)
            radius = int(math.ceil(math.sqrt((width//2)**2 + (height//2)**2)))
            for i in range(radius, 0, -1):
              pg.draw.circle(screen, (0,0,0), (width//2, height//2), i, 1)
              pg.display.flip()
            await lobby(websocket, res, False)
            return True

        elif hsquare == 5:
          await websocket.send("logout")
          await websocket.recv()
          display_menu()
          screen.blit(login, (width//2+10, height//4))
          screen.blit(signup, (width//2-261, height//4))
          pg.display.flip()
          pg.mouse.set_cursor(*pg.cursors.arrow)
          return False

        elif hsquare == 6:
          rs = await delete_account(websocket)
          return rs

        elif hsquare == 7:
          rs = await customize(websocket, appearance)
          if rs:
            appearance["nickname"] = rs[0]
            appearance["h"] = rs[1]
            appearance["s"] = rs[2]
            appearance["l"] = rs[3]
          display_menu()
          mainmenuicons()
          textbox(3*height//8+5, 3*width//5, col = (114, 247, 247), text = "Enter Code", textcol = (0, 200, 200))
          rtext(font2, f"Hi {appearance['nickname']} ({data[0]})", 105, color = (66, 245, 245))
          player = load("player.png", pwidth*2, pheight*2)
          pscale(player, 3*width//4, height//2, [appearance["h"], appearance["s"], appearance["l"]])
          pg.display.flip()

      if event.type == KEYDOWN:
        if event.key == K_BACKSPACE:
          inputs = inputs[:-1]
          if inputs == "":
            textbox((cur+2)*height//8+5, 3*width//5, col = (114, 247, 247), text = "Enter Code", textcol = (0, 200, 200))
          else: 
            textbox((cur+2)*height//8+5, 3*width//5, col = (114, 247, 247), text = inputs)
          pg.display.flip()
        elif event.unicode not in ",{}[]|\\":
          keys = pg.key.get_pressed()
          if keys[K_RSHIFT] or keys[K_LSHIFT]:
            inputs += event.unicode.upper()
          else:
            inputs += event.unicode
          if font3.size(inputs)[0] > 258 or len(inputs) > 32:
            inputs = inputs[:-1]
          if inputs == "":
            textbox((cur+2)*height//8+5, 3*width//5, col = (114, 247, 247), text = "Enter Code", textcol = (0, 200, 200))
          else: 
            textbox((cur+2)*height//8 +5, 3*width//5, col = (114, 247, 247), text = inputs)
          pg.display.flip()
    await asyncio.sleep(0.03)

async def program():
  global screen, size, width, height, font, font2
  uri = f"ws://rq2.duckdns.org:8765"
  try:
    async with websockets.connect(uri) as websocket:
      
      display_menu()

      screen.blit(login, (width//2+10, height//4))
      screen.blit(signup, (width//2-261, height//4))
      
      pg.display.flip()
      #bg = pg.image.load("lounge_temp.png").convert()
      pg.key.set_repeat()
      hoversquare = 0
      while True:
        x, y = pg.mouse.get_pos()
        if x in range(width//2-261, width//2-10) and y in range(height//4, height//4+71):
          if hoversquare in [0, 2]:
            hoversquare = 1
            pg.mouse.set_cursor(*pg.cursors.diamond)
            screen.blit(signup2, (width//2-261, height//4))
            screen.blit(login, (width//2+10, height//4))
            pg.display.flip()
        elif x in range(width//2+10, width//2+261) and y in range(height//4, height//4+71):
          if hoversquare in [0, 1]:
            hoversquare = 2
            pg.mouse.set_cursor(*pg.cursors.diamond)
            screen.blit(login2, (width//2+10, height//4))
            screen.blit(signup, (width//2-261, height//4))
            pg.display.flip()
        elif hoversquare != 0:
          screen.blit(signup, (width//2-261, height//4))
          screen.blit(login, (width//2+10, height//4))
          pg.display.flip()
          hoversquare = 0
          pg.mouse.set_cursor(*pg.cursors.arrow)

        for event in pg.event.get():
          if event.type == QUIT: 
            sys.exit()
          elif event.type == VIDEORESIZE:
            size = width, height = (event.w, event.h)
            screen = pg.display.set_mode(size, pg.RESIZABLE)
            display_menu()
            screen.blit(login, (width//2+10, height//4))
            screen.blit(signup, (width//2-261, height//4))
            pg.display.flip()
          elif event.type == MOUSEBUTTONUP:
            if hoversquare in [1, 2]:
              res = await prompt(websocket, 2-hoversquare)
              if res:
                while True:
                  r = await mainmenu(websocket, res)
                  if not r: break
          """
          elif event.type == pg.KEYDOWN and event.key == K_SPACE:
            spacestate = 1
          """
        """
        await websocket.send(f"m,{keys[K_DOWN]},{keys[K_UP]},{keys[K_LEFT]},{keys[K_RIGHT]},{spacestate}")
        jsondata = await websocket.recv()
        data = json.loads(jsondata)
        displaydata = data["player"]
        balls = data["ball"]
        screen.fill((0,0,0))
        ex = displaydata[name]["x"]-(400-16)
        why = displaydata[name]["y"]-(300-16)
        screen.blit(bg, (0,0), pg.Rect(ex, why, width, height))
        screen.blit(walls, (0,0), pg.Rect(ex, why, width, height))
        for ball in balls:
          screen.blit(pg.transform.rotate(bl, ball["tilt"]), (ball["x"]-ex, ball["y"]-why))

        todisplay = []
        top = []
        typemap = [(255, 0, 0), (0, 0, 255), (0, 255, 255)]
        for player in displaydata:
          px = displaydata[player]["x"]-ex
          py = displaydata[player]["y"]-why
          ptype = displaydata[player]["t"]
          pteam = displaydata[player]["e"]
          pscore = displaydata[player]["p"]
          if player == name:
            tx = (0, 128, 128)
            if pscore != points:
              points = pscore
              phrase_timer[0] = time.time()
              flags[0] = True
          else:
            tx = typemap[pteam]
          todisplay.append([px+ex, py+why, tx])
          pdir = displaydata[player]["d"]
          pxspeed = displaydata[player]["n"]
          pyspeed = displaydata[player]["m"]
          if player == name:
            top.append([pscore, player + " (You)", typemap[pteam]])
          else:
            top.append([pscore, player, typemap[pteam]])
          if player == name:
            player = player + " (You)"
          pwidth = font2.size(player)[0]//2
          screen.blit(font2.render(player, True, (255,255,255)), (px+16-pwidth, py-14))
          toblit = typelist[ptype][pdir][pxspeed>=0]
          if pteam != 2:
            toblit = toblit.copy()
            toblit.fill((100*(1-pteam), 0, 100*pteam), special_flags=pg.BLEND_RGB_ADD)
          screen.blit(toblit, (px, py))
        top.sort()
        top.reverse()
        top = top[:10]
        playermap = pg.Surface((200, 150), pg.SRCALPHA)
        playermap.fill((255,255,255,128))  
        screen.blit(playermap, (600, 0))
        screen.blit(miniwalls, (600, 0))
        for d in todisplay:
          ply = pg.Rect((d[0]//8)+600, d[1]//8, 4, 4) 
          pg.draw.rect(screen, d[2], ply)
        for ball in balls:
          pbl = pg.Rect((ball["x"]//8)+600, ball["y"]//8, 4, 4)
          pg.draw.rect(screen, (255, 255, 255), pbl)
        screen.blit(playermap, (0, 0))
        counter = 25
        text = font.render(f"RED {data['game']['red']}", True, (255,0,0))
        screen.blit(text, (1, 0))
        text = font.render(f"{data['game']['blue']} BLUE", True, (0,0,255))
        text_rect = text.get_rect()
        text_rect.right = 198
        screen.blit(text, text_rect)
        if data["game"]["blue"] == data["game"]["red"] == 14 and not prevscored:
          flags[1] = True
          prevscored = True
          phrase_timer[1] = time.time()
        if data["game"]["blue"] == data["game"]["red"] == 0 and prevscored:
          flags[2] = data["game"]["whowon"]
          phrase_timer[2] = time.time()
          prevscored = False
        for i in top:
          screen.blit(font2.render(i[1] + f" ({i[0]})", True, i[2]), (5, counter))
          counter += 10
        for i in range(3):
          if flags[i]:
            if time.time() - phrase_timer[i] < 3:
              words = ["You scored!", "Last goal wins!", flags[i]]
              text = font.render(words[i], True, (255,255,255))
              screen.blit(text, (300, 20+30*i))
            else:
              phrase_timer[i] = time.time()
              flags[i] = [False, ""][i == 2]
        """
        await asyncio.sleep(0.03)
  except Exception as error:
    if "code = 1000 (OK), no reason" not in str(error) and "code = 1006" not in str(error) and "code = 1011" not in str(error):
      print("".join(traceback.format_exception(type(error), error, error.__traceback__, 999)))
      return ""
    if "code" in str(error):
      return "Internal server error. Please try again later. "
    return "Client error. Please try again later. "

resstate = asyncio.get_event_loop().run_until_complete(program())
print(resstate)