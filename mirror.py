import pygame
import math

class Ray:
	def __init__(self, startpos, direction):
		self.startpos = startpos
		self.direction = direction
		self.dist = 3000
		self.lines = []

	def length(self, p1, p2):
		return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

	def calculate(self, mirrors):
		self.lines = []
		
		startpos = self.startpos
		direction = self.direction
		m = None
		min_pos = True
		count = 0

		while min_pos and count < 1000:
			count += 1
			found = False
			min_dist = float("inf")
			min_pos = None
			min_mirror = None

			for mirror in mirrors:
				if mirror == m:
					continue

				if pos := find_intersection((startpos, direction), ((mirror.x1, mirror.y1), (mirror.x2, mirror.y2))):
					d = self.length(pos, startpos)
					
					if d < min_dist:
						min_dist = d
						min_pos = pos
						min_mirror = mirror

			m = min_mirror

			if min_pos:
				self.lines.append((startpos, min_pos))
				v = min_mirror.reflection((startpos, min_pos), direction)
				startpos = min_pos
				direction = v[0] * self.dist + min_pos[0], v[1] * self.dist + min_pos[1]

		self.lines.append((startpos, direction))

	def draw(self):
		for l in self.lines:
			line(l[0][0], l[0][1], l[1][0], l[1][1])

class Sun:
	def __init__(self, count, fov=None, ray_len=500):
		self.pos = [0, 0]
		self.fov = fov if fov else math.pi * 2
		self.ray_len = ray_len
		self.rays = [Ray([0,0],[0,0]) for _ in range(count)]

		self.set_start_pos([100,0])

	def move(self, pos):
		self.pos = pos
		set_start_pos()			

	def set_start_pos(self, pos):
		ang = self.fov / len(self.rays)

		for i, ray in enumerate(self.rays):
			ray.startpos = pos
			ray.direction = self.ray_len * math.cos(ang * i) + pos[0], self.ray_len * math.sin(ang * i) + pos[1]

	def calculate(self, mirrors):
		for ray in self.rays:
			ray.calculate(mirrors)

	def draw(self):
		for ray in self.rays:
			ray.draw()

class Mirror:
	def __init__(self, x1, y1, x2, y2):
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2

		mv = [self.x2 - self.x1, self.y2 - self.y1]
		self.direction = [mv[0] / (self.length(mv) or 0.00001), mv[1] / (self.length(mv) or 0.00001)]

	def length(self, p1):
		return (p1[0] ** 2 + p1[1] ** 2) ** 0.5

	def reflection(self, line, mouse):
		rd = [line[1][0] - line[0][0], line[1][1] - line[0][1]]
		rd = [rd[0] / self.length(rd), rd[1] / self.length(rd)]

		scal = rd[0] * self.direction[0] + rd[1] * self.direction[1]

		reflected_d = [
			- (rd[0] - 2 * scal * self.direction[0]),
			- (rd[1] - 2 * scal * self.direction[1])
		]

		return reflected_d

enable = True

w = 1920
h = 1080

screen = pygame.display.set_mode((w, h))

def find_intersection(line1, line2):
	s1 = line1[0]
	e1 = line1[1]

	s2 = line2[0]
	e2 = line2[1]

	dir1 = (e1[0] - s1[0], e1[1] - s1[1])
	dir2 = (e2[0] - s2[0], e2[1] - s2[1])

	a1 = -dir1[1]
	b1 = dir1[0]
	d1 = - (a1 * s1[0] + b1 * s1[1])

	a2 = -dir2[1]
	b2 = dir2[0]
	d2 = - (a2 * s2[0] + b2 * s2[1])

	s1_l2_st = a2 * s1[0] + b2 * s1[1] + d2
	s1_l2_ed = a2 * e1[0] + b2 * e1[1] + d2

	s2_l1_st = a1 * s2[0] + b1 * s2[1] + d1
	s2_l1_ed = a1 * e2[0] + b1 * e2[1] + d1

	if (s1_l2_st * s1_l2_ed >= 0 or s2_l1_st * s2_l1_ed >= 0):
		return False

	u = s1_l2_st / (s1_l2_st - s1_l2_ed);

	return (s1[0] + u * dir1[0], s1[1] +  u * dir1[1])

def line(x1, y1, x2, y2, c=None):
	c = c if c else (250, 250, 0)
	pygame.draw.line(screen, c, (x1, y1), (x2, y2))

def draw_vec(vec, pos, c=None, l=10):
	line(vec[0] * l + pos[0], vec[1] * l + pos[1], pos[0], pos[1], c)

def main():
	enable = True

	suns = [Sun(100, 0, 500)]
	points = [((x * 2) ** 2 + 200, (x * 30) + 600) for x in range(-10, 10)]

	mirrors = [
		Mirror(*p1, *p2) for p1, p2 in zip(points[:-1], points[1:])
	]

	indexes = []
	for i, mirror1 in enumerate(mirrors):
		for j, mirror2 in enumerate(mirrors):
			if i == j:
				continue

			if mirror1.x1 == mirror2.x1 and mirror1.x2 == mirror2.x2 and mirror1.y1 == mirror2.y1 and mirror1.y2 == mirror2.y2:
				indexes.insert(0, i)
			
	for index in indexes:
		mirrors.pop(index)

	while enable:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				enable = False

			elif event.type == pygame.MOUSEMOTION:
				suns[0].set_start_pos(event.pos)

		screen.fill((0, 0, 0))

		for sun in suns:
			sun.calculate(mirrors)
			sun.draw()

		for mirror in mirrors:
			pygame.draw.line(screen, (120, 120, 120), (mirror.x1, mirror.y1), (mirror.x2, mirror.y2)) # Mirror
		
		pygame.display.flip()

if __name__ == "__main__":
	main()