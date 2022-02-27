import pygame, time, random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
INITIAL_PLAYER_X = 400 
INITIAL_PLAYER_Y = 340
BACKGROUND_COLOR = (0,0,0)
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
FPS_CLOCK = pygame.time.Clock()
MAX_ASTEROID_COUNT = 5

bullet_velocity = -8
bullet_reload_time = 0.1
bullet_damage = 60
player_speed = 4
asteroid_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
pygame.display.flip()

#Assets of the game
player_img_1 = pygame.image.load('assets/Ship_1.png')
player_img_2 = pygame.image.load('assets/Ship_2.png')
player_img_3 = pygame.image.load('assets/Ship_3.png')
player_img_4 = pygame.image.load('assets/Ship_4.png')
bullet_img = pygame.image.load('assets/bullet.png')
big_asteroid_1 = pygame.image.load('assets/big_asteroid_1.png')
small_1_asteroid_1 = pygame.image.load('assets/small_1_asteroid_1.png') 
small_2_asteroid_1 = pygame.image.load('assets/small_2_asteroid_1.png') 
small_3_asteroid_1 = pygame.image.load('assets/small_3_asteroid_1.png')

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		self.image = bullet_img
		self.rect = bullet_img.get_rect(midtop=(x, y))
		self.damage = bullet_damage

	def update(self):
		if self.rect.top < -30:
			self.kill()
		else:
			self.rect.move_ip(0, bullet_velocity)

class Player(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		self.x = x
		self.y = y
		self.health = 300
		self.image_list = [player_img_1, player_img_2, player_img_3, player_img_4]
		self.index = 0
		self.image = self.image_list[self.index]
		self.rect = self.image.get_rect(center=(self.x, self.y))
		self.reloaded = True
		self.last_shot_time = 0
		self.alive = True
		player_group.add(self)

	def update(self, speed):
		self.index += speed
 
		if self.index >= len(self.image_list):
			self.index = 0

		self.image = self.image_list[int(self.index)]

class Asteroid(pygame.sprite.Sprite):
	asteroid_count = 0
	asteroid_kill_count = 0
	@staticmethod
	def make_asteroid():
		random_vel = random.choice([2, 3, 3, 5, 2, 3, 2])
		random_x = random.randint(0, 800)
		asteroid_group.add(Asteroid(random_x, -40 , 0, random_vel))

	def __init__(self, x, y, x_velocity, y_velocity):
		super().__init__()
		Asteroid.asteroid_count += 1
		self.x = 100
		self.y = 100
		self.x_velocity = x_velocity
		self.y_velocity = y_velocity
		self.health = 250
		self.image = big_asteroid_1
		self.rect = self.image.get_rect(topleft=(x, y))
 
	def update(self):
		if self.rect.bottom > SCREEN_HEIGHT+30 or self.rect.left < -30 or self.rect.right > SCREEN_WIDTH+30:
			self.kill()
			Asteroid.asteroid_count -= 1
		else:
			pygame.transform.rotate(self.image, 3)
			self.rect.move_ip(self.x_velocity, self.y_velocity)

class SmallAsteroid(Asteroid):
	def __init__(self, x, y, x_velocity, y_velocity, image):
		super().__init__(x, y, x_velocity, y_velocity)
		self.health = 100
		self.image = image
		self.rect = self.image.get_rect(center=(x, y))
		asteroid_group.add(self)

PLAYER = Player(INITIAL_PLAYER_X, INITIAL_PLAYER_Y)

def draw():
	bullet_group.update()
	player_group.update(0.25)
	asteroid_group.update()

	bullet_group.draw(SCREEN)
	player_group.draw(SCREEN)
	asteroid_group.draw(SCREEN)

def check_collision():
	collide_asteroid = pygame.sprite.groupcollide(asteroid_group, bullet_group, dokilla=False, dokillb=True)
	collide_player = pygame.sprite.groupcollide(player_group, asteroid_group, dokilla=False, dokillb=True)
	asteroid_kill_count = 0
	
	for collided in collide_asteroid:
		if collided.health <= 0:
			Asteroid.asteroid_count -= 1
			Asteroid.asteroid_kill_count += 1
			random_num = random.randint(1, 6)
			if random_num == 6:
				x, y = collided.rect.center
				asteroid_group.add(SmallAsteroid(x, y+5, 0, 2, small_1_asteroid_1))
				asteroid_group.add(SmallAsteroid(x+3, y+5, 3, -2, small_2_asteroid_1))
				asteroid_group.add(SmallAsteroid(x-3, y, -3, 0, small_3_asteroid_1))

			collided.kill()

		collided.health -= bullet_damage 

	for collided in collide_player:
		if PLAYER.health > 0:
			PLAYER.health -= 100
		else:
			PLAYER.alive = False
			collided.kill()

def main():
	RUNNING = True

	#Game loop
	while RUNNING:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				RUNNING = False

		key = pygame.key.get_pressed()
		if PLAYER.alive:
			if key[pygame.K_LEFT]:
				if PLAYER.rect.left <= 0:
					pass
				else:
					PLAYER.rect.move_ip(-player_speed, 0)

			if key[pygame.K_RIGHT]:
				if PLAYER.rect.right >= SCREEN_WIDTH:
					pass
				else:
					PLAYER.rect.move_ip(player_speed, 0)

			if key[pygame.K_UP]:
				if PLAYER.rect.top <= 0:
					pass
				else:
					PLAYER.rect.move_ip(0, -player_speed)

			if key[pygame.K_DOWN]:
				if PLAYER.rect.bottom >= SCREEN_HEIGHT:
					pass
				else:
					PLAYER.rect.move_ip(0, player_speed)

			if key[pygame.K_SPACE]:
				player_coordinates = PLAYER.rect.midtop 
				if PLAYER.reloaded:
					bullet_group.add(Bullet(player_coordinates[0], player_coordinates[1]))
					PLAYER.last_shot_time = time.time()
					PLAYER.reloaded = False
				else:
					if time.time() - PLAYER.last_shot_time > bullet_reload_time: 
						PLAYER.reloaded = True

		if Asteroid.asteroid_count < MAX_ASTEROID_COUNT:
			Asteroid.make_asteroid()

		SCREEN.fill(BACKGROUND_COLOR)
		FPS_CLOCK.tick(FPS)

		draw()
		check_collision()
		pygame.display.update()

if __name__ == '__main__':
	main()
print(Asteroid.asteroid_count)