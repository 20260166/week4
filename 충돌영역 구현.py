import pygame
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hitbox Visualization (WASD)")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

def draw_text(text, x, y):
    img = font.render(text, True, (0,0,0))
    screen.blit(img, (x, y))

# 중심 좌표
player_center = [300, 300]
enemy_center = [500, 300]

size = 80
angle = 0
speed = 3

def get_rect(center, size):
    return pygame.Rect(center[0]-size//2, center[1]-size//2, size, size)

# 원형 충돌
def circle_collision(c1, c2):
    dx = c1[0] - c2[0]
    dy = c1[1] - c2[1]
    dist = math.sqrt(dx*dx + dy*dy)
    return dist < (size//2 + size//2)

# OBB 꼭짓점
def get_obb(center, size, angle):
    cx, cy = center
    rad = math.radians(angle)
    half = size / 2

    corners = []
    for dx, dy in [(-half,-half),(half,-half),(half,half),(-half,half)]:
        x = cx + dx*math.cos(rad) - dy*math.sin(rad)
        y = cy + dx*math.sin(rad) + dy*math.cos(rad)
        corners.append((x, y))
    return corners

# OBB 충돌 (SAT)
def obb_collision(c1, c2):
    def axes(c):
        result = []
        for i in range(len(c)):
            p1 = c[i]
            p2 = c[(i+1)%len(c)]
            edge = (p2[0]-p1[0], p2[1]-p1[1])
            normal = (-edge[1], edge[0])
            length = math.hypot(normal[0], normal[1])
            result.append((normal[0]/length, normal[1]/length))
        return result

    def project(corners, axis):
        dots = [corner[0]*axis[0] + corner[1]*axis[1] for corner in corners]
        return min(dots), max(dots)

    for axis in axes(c1) + axes(c2):
        min1, max1 = project(c1, axis)
        min2, max2 = project(c2, axis)

        if max1 < min2 or max2 < min1:
            return False
    return True

running = True
while running:
    screen.fill((255,255,255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # 👉 WASD 이동
    if keys[pygame.K_a]:
        player_center[0] -= speed
    if keys[pygame.K_d]:
        player_center[0] += speed
    if keys[pygame.K_w]:
        player_center[1] -= speed
    if keys[pygame.K_s]:
        player_center[1] += speed

    # 👉 적 회전
    if keys[pygame.K_z]:
        angle += 3
    else:
        angle += 0.5

    # 🔴 AABB
    player_rect = get_rect(player_center, size)
    enemy_rect = get_rect(enemy_center, size)
    aabb_hit = player_rect.colliderect(enemy_rect)

    # 🔵 원형
    circle_hit = circle_collision(player_center, enemy_center)

    # 🟢 OBB
    player_obb = get_obb(player_center, size, 0)
    enemy_obb = get_obb(enemy_center, size, angle)
    obb_hit = obb_collision(player_obb, enemy_obb)

    # 👉 배경색
    if obb_hit:
        screen.fill((255,150,150))
    elif circle_hit:
        screen.fill((255,255,150))
    elif aabb_hit:
        screen.fill((150,200,255))

    # 🎯 실제 오브젝트
    pygame.draw.rect(screen, (180,180,180), player_rect)
    pygame.draw.rect(screen, (180,180,180), enemy_rect)

    # 🔴 AABB
    pygame.draw.rect(screen, (255,0,0), player_rect, 2)
    pygame.draw.rect(screen, (255,0,0), enemy_rect, 2)

    # 🔵 원형
    pygame.draw.circle(screen, (0,0,255), player_center, size//2, 2)
    pygame.draw.circle(screen, (0,0,255), enemy_center, size//2, 2)

    # 🟢 OBB
    pygame.draw.polygon(screen, (0,255,0), player_obb, 2)
    pygame.draw.polygon(screen, (0,255,0), enemy_obb, 2)

    # 중심점
    pygame.draw.circle(screen, (0,0,0), player_center, 4)
    pygame.draw.circle(screen, (0,0,0), enemy_center, 4)

    # 텍스트
    if aabb_hit:
        draw_text("AABB HIT", 10, 10)
    if circle_hit:
        draw_text("Circle HIT", 10, 40)
    if obb_hit:
        draw_text("OBB HIT", 10, 70)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()