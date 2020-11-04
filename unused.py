saved = {}
for lx in range(101):
  for event in pg.event.get():
    if event.type == QUIT:
      sys.exit()
  plate = pg.Surface((401, 401), SRCALPHA).convert_alpha()
  for r in range(101):
    for theta in range(360):
      outputs = colorsys.hls_to_rgb(theta/360, lx/100, r/100)
      bruh = [[theta], [theta, theta+0.5], [theta, theta+0.33, theta+0.66], [theta, theta+0.25, theta+0.5, theta+0.75]][min(r//25, 3)]
      for t in bruh:
        fx = int(round(2*r*math.cos(t*math.pi/180)+200))
        fy = int(round(2*r*math.sin(t*math.pi/180)+200))
        plate.fill((int(round(outputs[0]*255)), int(round(outputs[1]*255)), int(round(outputs[2]*255))), ((fx, fy), (2, 2)))
  pg.image.save(plate, f"circles/{lx}.png")