import pygame
import random
import math

width, height = 800, 600
num_balls = 3
air_res = 0.999
damping = 0.98
g = -10

pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()


class Ball:
    def __init__(self, x, y, r, color):
        self.x = x
        self.y = y
        self.r = r
        self.color = color
        self.vx = random.uniform(1, 5)
        self.vy = random.uniform(1, 5)

    def move(self, dt, g):
        self.vy -= g * dt

        self.vx *= air_res
        self.vy *= air_res

        self.x += self.vx * dt
        self.y += self.vy * dt

        # odbijanie:
        # lewa krawedz za bardzo w lewo
        if self.x - self.r < 0:
            self.x = self.r  # przesuwamy srodek o r blisko od krawedzi
            self.vx *= -damping  # wytracamy predkosc,
            # ale tez odbijamy pileczke w poziomie (stad -)

        # prawa krawedz za bardzo w prawo
        elif self.x + self.r > width:
            self.x = width - self.r
            self.vx *= -damping

        # analogicznie jak wczesniej
        if self.y - self.r < 0:
            self.y = self.r
            self.vy *= -damping
        elif self.y + self.r > height:
            self.y = height - self.r
            self.vy *= -damping

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.r)

    def is_clicked(self, pos):
        mx, my = pos
        return math.hypot(self.x - mx, self.y - my) <= self.r


def handle_obstacle_collision(ball, obstacle, damping=0.9):
    # najbliższy punkt na prostokącie do środka kulki
    closest_x = max(obstacle.left, min(ball.x, obstacle.right))
    closest_y = max(obstacle.top,  min(ball.y, obstacle.bottom))

    dx, dy = ball.x - closest_x, ball.y - closest_y #wektor od prostokata do kulki
    dist = math.hypot(dx, dy) # odleglosc

    if dist < ball.r:
        # przesunięcie kulki poza przeszkodę
        overlap = ball.r - dist #o tyle "nachodza" na siebie
        if dist != 0: #wektor w kierunku odbicia
            dx /= dist
            dy /= dist
        else:
            dx, dy = 1, 0  # srodek dokladnie na krawedzi
        ball.x += dx * overlap
        ball.y += dy * overlap
        # przesuwamy pilke o ten nowy wektor

        # odbicie predkosci
        dot = ball.vx * dx + ball.vy * dy
        ball.vx -= 2 * dot * dx
        ball.vy -= 2 * dot * dy
        #odbicie wektora predkosci

        # damping - wytracenie predkosci
        ball.vx *= damping
        ball.vy *= damping


def handle_collisions(balls):
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            b1, b2 = balls[i], balls[j]
            dx, dy = b2.x - b1.x, b2.y - b1.y
            dist = math.hypot(dx, dy)
            min_dist = b1.r + b2.r

            if dist < min_dist:
                # normalizowany wektor miedzy kulkami
                if dist != 0:
                    nx, ny = dx / dist, dy / dist
                else:
                    nx, ny = 1, 0

                # proste odbicie prędkości wzdłuż normalnego kierunku
                v1n = b1.vx * nx + b1.vy * ny # predkosci wzdluz linii kolizji
                v2n = b2.vx * nx + b2.vy * ny
                dv = v1n - v2n # roznica predkosci wzdluz kierunku
                b1.vx -= dv * nx
                b1.vy -= dv * ny
                b2.vx += dv * nx
                b2.vy += dv * ny

                # korekcja pozycji, zeby kulki sie nie przenikaly
                overlap = (min_dist - dist) / 2
                b1.x -= nx * overlap
                b1.y -= ny * overlap
                b2.x += nx * overlap
                b2.y += ny * overlap


obstacles = [
    pygame.Rect(200, 250, 100, 20),
    pygame.Rect(500, 400, 150, 20)
]

# tworzenie pileczek
balls = [Ball(random.randint(50, width - 50),
              random.randint(50, height - 50),
              random.randint(15, 25),
              [random.randint(100, 255) for _ in range(3)]) for _ in range(num_balls)]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for b in balls:
                if b.is_clicked(pos):
                    b.vx *= -1
                    b.vy *= -1


    screen.fill((30, 30, 30))

    # rysuj przeszkody
    for obs in obstacles:
        pygame.draw.rect(screen, (150, 150, 150), obs)

    # ruch piłeczek
    dt = clock.get_time() / 100.0
    for b in balls:
        b.move(dt,g)

        # odbicia od przeszkód
        for obs in obstacles:
            handle_obstacle_collision(b, obs)
        b.draw()

    handle_collisions(balls)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
