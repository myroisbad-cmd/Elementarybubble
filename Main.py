import pygame
import math
import random
import time
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple

# Initialisation
pygame.init()

# Configuration
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 1920
FPS = 60
GAME_DURATION = 61.0  # 1 minute 1 seconde
DISRUPTION_INTERVAL = 12.0  # Toutes les 12 secondes
BONUS_SPAWN_INTERVAL = 8.0  # Bonus toutes les 8 secondes

class BallType(Enum):
    FIRE = "fire"
    ICE = "ice"
    METAL = "metal"
    LIGHTNING = "lightning"
    POISON = "poison"

class BonusType(Enum):
    SPEED_BOOST = "speed"
    HEALTH_KIT = "health"
    SHIELD = "shield"
    MULTIPLY = "multiply"
    RAGE = "rage"
    FREEZE_BLAST = "freeze"

@dataclass
class Color:
    r: int
    g: int
    b: int
    
    def to_tuple(self):
        return (self.r, self.g, self.b)
    
    def lerp(self, other, t):
        return Color(
            int(self.r + (other.r - self.r) * t),
            int(self.g + (other.g - self.g) * t),
            int(self.b + (other.b - self.b) * t)
        )

# Couleurs
COLORS = {
    BallType.FIRE: Color(255, 100, 0),
    BallType.ICE: Color(100, 200, 255),
    BallType.METAL: Color(150, 150, 150),
    BallType.LIGHTNING: Color(255, 255, 100),
    BallType.POISON: Color(100, 255, 100)
}

BONUS_COLORS = {
    BonusType.SPEED_BOOST: Color(255, 255, 0),
    BonusType.HEALTH_KIT: Color(0, 255, 0),
    BonusType.SHIELD: Color(0, 150, 255),
    BonusType.MULTIPLY: Color(255, 0, 255),
    BonusType.RAGE: Color(255, 50, 50),
    BonusType.FREEZE_BLAST: Color(150, 255, 255)
}

# Système de dégâts (rock-paper-scissors étendu)
DAMAGE_MULTIPLIERS = {
    BallType.FIRE: {BallType.ICE: 2.5, BallType.POISON: 1.8, BallType.METAL: 0.4, BallType.LIGHTNING: 0.7},
    BallType.ICE: {BallType.METAL: 2.5, BallType.FIRE: 0.4, BallType.LIGHTNING: 1.8, BallType.POISON: 0.7},
    BallType.METAL: {BallType.LIGHTNING: 2.5, BallType.ICE: 0.4, BallType.POISON: 1.8, BallType.FIRE: 1.2},
    BallType.LIGHTNING: {BallType.POISON: 2.5, BallType.METAL: 0.4, BallType.FIRE: 1.2, BallType.ICE: 0.7},
    BallType.POISON: {BallType.FIRE: 2.5, BallType.LIGHTNING: 0.4, BallType.ICE: 1.2, BallType.METAL: 0.7}
}

class Arena:
    def __init__(self):
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2
        self.shape_type = "hexagon"  # hexagon, octagon, diamond
        self.walls = []
        self.generate_shape()
        
    def generate_shape(self):
        self.walls = []
        if self.shape_type == "hexagon":
            self.create_hexagon()
        elif self.shape_type == "octagon":
            self.create_octagon()
        elif self.shape_type == "diamond":
            self.create_diamond()
    
    def create_hexagon(self):
        radius = 400
        center_x, center_y = self.center_x, self.center_y + 200
        for i in range(6):
            angle1 = i * math.pi / 3
            angle2 = (i + 1) * math.pi / 3
            x1 = center_x + radius * math.cos(angle1)
            y1 = center_y + radius * math.sin(angle1)
            x2 = center_x + radius * math.cos(angle2)
            y2 = center_y + radius * math.sin(angle2)
            self.walls.append(((x1, y1), (x2, y2)))
    
    def create_octagon(self):
        radius = 380
        center_x, center_y = self.center_x, self.center_y + 200
        for i in range(8):
            angle1 = i * math.pi / 4
            angle2 = (i + 1) * math.pi / 4
            x1 = center_x + radius * math.cos(angle1)
            y1 = center_y + radius * math.sin(angle1)
            x2 = center_x + radius * math.cos(angle2)
            y2 = center_y + radius * math.sin(angle2)
            self.walls.append(((x1, y1), (x2, y2)))
    
    def create_diamond(self):
        center_x, center_y = self.center_x, self.center_y + 200
        width, height = 600, 800
        # Diamond shape (4 walls)
        self.walls = [
            ((center_x, center_y - height//2), (center_x + width//2, center_y)),  # Top-right
            ((center_x + width//2, center_y), (center_x, center_y + height//2)),  # Bottom-right
            ((center_x, center_y + height//2), (center_x - width//2, center_y)),  # Bottom-left
            ((center_x - width//2, center_y), (center_x, center_y - height//2))   # Top-left
        ]
    
    def check_collision(self, ball):
        collided = False
        for wall in self.walls:
            if self.ball_wall_collision(ball, wall):
                collided = True
        return collided
    
    def ball_wall_collision(self, ball, wall):
        (x1, y1), (x2, y2) = wall
        
        # Vecteur du mur
        wall_dx = x2 - x1
        wall_dy = y2 - y1
        wall_length = math.sqrt(wall_dx*wall_dx + wall_dy*wall_dy)
        
        if wall_length == 0:
            return False
        
        # Vecteur normal au mur
        normal_x = -wall_dy / wall_length
        normal_y = wall_dx / wall_length
        
        # Distance du centre de la balle au mur
        to_ball_x = ball.x - x1
        to_ball_y = ball.y - y1
        
        # Projection sur le mur
        wall_projection = (to_ball_x * wall_dx + to_ball_y * wall_dy) / wall_length
        
        # Point le plus proche sur le mur
        if wall_projection < 0:
            closest_x, closest_y = x1, y1
        elif wall_projection > wall_length:
            closest_x, closest_y = x2, y2
        else:
            closest_x = x1 + (wall_projection / wall_length) * wall_dx
            closest_y = y1 + (wall_projection / wall_length) * wall_dy
        
        # Distance à ce point
        dist_x = ball.x - closest_x
        dist_y = ball.y - closest_y
        distance = math.sqrt(dist_x*dist_x + dist_y*dist_y)
        
        if distance <= ball.radius:
            # Collision détectée - rebond
            if distance > 0:
                # Normaliser le vecteur de collision
                norm_x = dist_x / distance
                norm_y = dist_y / distance
                
                # Repositionner la balle
                ball.x = closest_x + norm_x * ball.radius
                ball.y = closest_y + norm_y * ball.radius
                
                # Calculer la nouvelle vitesse (réflexion)
                dot_product = ball.vx * norm_x + ball.vy * norm_y
                ball.vx = ball.vx - 2 * dot_product * norm_x
                ball.vy = ball.vy - 2 * dot_product * norm_y
                
                # ACCÉLÉRATION À CHAQUE REBOND !
                speed_multiplier = 1.15  # +15% de vitesse
                ball.vx *= speed_multiplier
                ball.vy *= speed_multiplier
                
                # Limiter la vitesse maximale
                max_speed = 800
                current_speed = math.sqrt(ball.vx*ball.vx + ball.vy*ball.vy)
                if current_speed > max_speed:
                    ball.vx = (ball.vx / current_speed) * max_speed
                    ball.vy = (ball.vy / current_speed) * max_speed
                
                return True
        
        return False
    
    def draw(self, screen):
        # Dessiner l'arène avec un effet de lueur
        for wall in self.walls:
            (x1, y1), (x2, y2) = wall
            
            # Ligne principale épaisse
            pygame.draw.line(screen, (255, 255, 255), (int(x1), int(y1)), (int(x2), int(y2)), 8)
            
            # Effet de lueur
            glow_colors = [(100, 150, 255), (150, 200, 255), (200, 230, 255)]
            for i, color in enumerate(glow_colors):
                pygame.draw.line(screen, color, (int(x1), int(y1)), (int(x2), int(y2)), 8 + i * 4)
        
        # Dessiner les coins avec des cercles lumineux
        for wall in self.walls:
            (x1, y1), (x2, y2) = wall
            pygame.draw.circle(screen, (255, 255, 100), (int(x1), int(y1)), 6)

class Bonus:
    def __init__(self, x, y, bonus_type: BonusType):
        self.x = x
        self.y = y
        self.type = bonus_type
        self.color = BONUS_COLORS[bonus_type]
        self.radius = 20
        self.pulse = 0
        self.collected = False
        self.life_time = 15.0  # Disparaît après 15 secondes
        self.spawn_time = time.time()
        
    def update(self, dt):
        self.pulse += dt * 5
        current_time = time.time()
        if current_time - self.spawn_time > self.life_time:
            return False
        return True
    
    def check_collision(self, ball):
        dx = ball.x - self.x
        dy = ball.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < ball.radius + self.radius:
            self.apply_effect(ball)
            self.collected = True
            return True
        return False
    
    def apply_effect(self, ball):
        if self.type == BonusType.SPEED_BOOST:
            ball.vx *= 1.5
            ball.vy *= 1.5
            ball.speed_boost_time = time.time() + 5.0
            
        elif self.type == BonusType.HEALTH_KIT:
            ball.health = min(ball.max_health, ball.health + 50)
            
        elif self.type == BonusType.SHIELD:
            ball.shield_time = time.time() + 8.0
            ball.shield_strength = 3
            
        elif self.type == BonusType.MULTIPLY:
            # Sera géré par le jeu principal
            pass
            
        elif self.type == BonusType.RAGE:
            ball.rage_time = time.time() + 10.0
            ball.damage_multiplier = 3.0
            
        elif self.type == BonusType.FREEZE_BLAST:
            ball.freeze_blast_ready = True
    
    def draw(self, screen):
        if self.collected:
            return
            
        # Effet de pulsation
        pulse_size = self.radius + math.sin(self.pulse) * 5
        
        # Lueur
        glow_surf = pygame.Surface((int(pulse_size * 4), int(pulse_size * 4)), pygame.SRCALPHA)
        glow_color = (*self.color.to_tuple(), 100)
        pygame.draw.circle(glow_surf, glow_color, (int(pulse_size * 2), int(pulse_size * 2)), int(pulse_size * 2))
        screen.blit(glow_surf, (int(self.x - pulse_size * 2), int(self.y - pulse_size * 2)))
        
        # Corps principal
        pygame.draw.circle(screen, self.color.to_tuple(), (int(self.x), int(self.y)), int(pulse_size))
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), int(pulse_size), 3)
        
        # Icône du bonus
        self.draw_icon(screen)
    
    def draw_icon(self, screen):
        # Dessiner des icônes simples pour chaque type de bonus
        x, y = int(self.x), int(self.y)
        
        if self.type == BonusType.SPEED_BOOST:
            # Flèches de vitesse
            points = [(x-8, y), (x+8, y-6), (x+8, y+6)]
            pygame.draw.polygon(screen, (255, 255, 255), points)
            
        elif self.type == BonusType.HEALTH_KIT:
            # Croix de soin
            pygame.draw.rect(screen, (255, 255, 255), (x-2, y-8, 4, 16))
            pygame.draw.rect(screen, (255, 255, 255), (x-8, y-2, 16, 4))
            
        elif self.type == BonusType.SHIELD:
            # Bouclier
            points = [(x, y-10), (x-8, y-5), (x-8, y+5), (x, y+10), (x+8, y+5), (x+8, y-5)]
            pygame.draw.polygon(screen, (255, 255, 255), points, 2)
            
        elif self.type == BonusType.MULTIPLY:
            # Signe multiplication
            pygame.draw.line(screen, (255, 255, 255), (x-6, y-6), (x+6, y+6), 3)
            pygame.draw.line(screen, (255, 255, 255), (x-6, y+6), (x+6, y-6), 3)
            
        elif self.type == BonusType.RAGE:
            # Éclairs de rage
            points = [(x-5, y-8), (x, y), (x-3, y), (x+5, y+8), (x, y), (x+3, y)]
            pygame.draw.lines(screen, (255, 255, 255), False, points, 2)
            
        elif self.type == BonusType.FREEZE_BLAST:
            # Flocon de neige
            pygame.draw.line(screen, (255, 255, 255), (x-8, y), (x+8, y), 2)
            pygame.draw.line(screen, (255, 255, 255), (x, y-8), (x, y+8), 2)
            pygame.draw.line(screen, (255, 255, 255), (x-6, y-6), (x+6, y+6), 2)
            pygame.draw.line(screen, (255, 255, 255), (x-6, y+6), (x+6, y-6), 2)

class Particle:
    def __init__(self, x, y, vx, vy, color, life, effect_type="normal"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.effect_type = effect_type
        self.size = random.uniform(2, 8)
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        
        # Friction
        self.vx *= 0.98
        self.vy *= 0.98
        
        return self.life > 0
    
    def draw(self, screen):
        if self.life <= 0:
            return
            
        alpha = max(0, min(1, self.life / self.max_life))
        size = int(self.size * alpha)
        if size > 0:
            color = (
                max(0, min(255, self.color.r)),
                max(0, min(255, self.color.g)),
                max(0, min(255, self.color.b)),
                int(255 * alpha)
            )
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (size, size), size)
            screen.blit(surf, (int(self.x - size), int(self.y - size)))

class Ball:
    def __init__(self, x, y, ball_type: BallType):
        self.x = x
        self.y = y
        self.vx = random.uniform(-150, 150)
        self.vy = random.uniform(-150, 150)
        self.type = ball_type
        self.color = COLORS[ball_type]
        self.radius = random.uniform(15, 25)
        self.health = 100.0
        self.max_health = 100.0
        self.last_attack = 0
        self.attack_cooldown = 0.8
        self.glow_intensity = 0
        
        # Effets des bonus
        self.speed_boost_time = 0
        self.shield_time = 0
        self.shield_strength = 0
        self.rage_time = 0
        self.damage_multiplier = 1.0
        self.freeze_blast_ready = False
        
    def update(self, dt, balls, particles, disruptions, arena):
        # Mouvement de base
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Vérifier les collisions avec l'arène
        arena.check_collision(self)
        
        # Effets des perturbations
        for disruption in disruptions:
            disruption.apply_to_ball(self)
        
        # Gestion des effets de bonus
        current_time = time.time()
        
        # Speed boost
        if current_time > self.speed_boost_time:
            self.speed_boost_time = 0
            
        # Shield
        if current_time > self.shield_time:
            self.shield_time = 0
            self.shield_strength = 0
            
        # Rage
        if current_time > self.rage_time:
            self.rage_time = 0
            self.damage_multiplier = 1.0
        
        # Comportements spécifiques au type
        self.apply_type_behavior(dt, balls)
        
        # Attaquer les autres balles
        self.attack_nearby_balls(balls, particles)
        
        # Particules de traînée
        self.create_trail_particles(particles)
        
        # Mise à jour de l'effet de lueur
        self.glow_intensity = (math.sin(time.time() * 5) + 1) * 0.5
        
    def apply_type_behavior(self, dt, balls):
        if self.type == BallType.FIRE:
            # Accélération vers les balles de glace
            for ball in balls:
                if ball != self and ball.type == BallType.ICE:
                    dx = ball.x - self.x
                    dy = ball.y - self.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < 200:
                        force = 80 / (dist + 1)
                        self.vx += (dx / dist) * force * dt
                        self.vy += (dy / dist) * force * dt
                        
        elif self.type == BallType.ICE:
            # Ralentissement graduel (mais pas trop avec les rebonds qui accélèrent)
            self.vx *= 0.999
            self.vy *= 0.999
            
        elif self.type == BallType.METAL:
            # Attraction mutuelle avec autres métaux
            for ball in balls:
                if ball != self and ball.type == BallType.METAL:
                    dx = ball.x - self.x
                    dy = ball.y - self.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < 150:
                        force = 50 / (dist + 1)
                        self.vx += (dx / dist) * force * dt
                        self.vy += (dy / dist) * force * dt
                        
        elif self.type == BallType.LIGHTNING:
            # Mouvement erratique
            if random.random() < 0.08:
                self.vx += random.uniform(-80, 80)
                self.vy += random.uniform(-80, 80)
                
        elif self.type == BallType.POISON:
            # Empoisonne les balles proches
            for ball in balls:
                if ball != self and self.distance_to(ball) < 100:
                    if ball.shield_strength <= 0:
                        ball.health -= 8 * dt
    
    def attack_nearby_balls(self, balls, particles):
        current_time = time.time()
        if current_time - self.last_attack < self.attack_cooldown:
            return
            
        for ball in balls:
            if ball != self and self.distance_to(ball) < self.radius + ball.radius + 15:
                damage = self.calculate_damage(ball)
                
                # Appliquer les dégâts (en tenant compte du bouclier)
                if ball.shield_strength > 0:
                    ball.shield_strength -= 1
                    damage *= 0.3  # Réduction des dégâts
                
                ball.take_damage(damage)
                self.last_attack = current_time
                
                # Freeze blast
                if self.freeze_blast_ready:
                    self.freeze_blast(balls, particles)
                    self.freeze_blast_ready = False
                
                # Effet visuel d'attaque
                self.create_attack_particles(ball, particles)
                break
    
    def freeze_blast(self, balls, particles):
        # Geler toutes les balles dans un rayon
        for ball in balls:
            if ball != self and self.distance_to(ball) < 200:
                ball.vx *= 0.1
                ball.vy *= 0.1
                
        # Effet visuel spectaculaire
        for _ in range(30):
            particles.append(Particle(
                self.x,
                self.y,
                random.uniform(-400, 400),
                random.uniform(-400, 400),
                Color(150, 255, 255),
                random.uniform(1.0, 2.5)
            ))
    
    def calculate_damage(self, target):
        base_damage = 25
        multiplier = DAMAGE_MULTIPLIERS[self.type].get(target.type, 1.0)
        return base_damage * multiplier * self.damage_multiplier
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
    def distance_to(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx*dx + dy*dy)
    
    def create_trail_particles(self, particles):
        if random.random() < 0.4:
            # Particules spéciales selon les bonus actifs
            trail_color = self.color
            if self.speed_boost_time > 0:
                trail_color = Color(255, 255, 100)
            elif self.rage_time > 0:
                trail_color = Color(255, 100, 100)
                
            particles.append(Particle(
                self.x + random.uniform(-self.radius, self.radius),
                self.y + random.uniform(-self.radius, self.radius),
                random.uniform(-80, 80),
                random.uniform(-80, 80),
                trail_color,
                random.uniform(0.5, 1.8)
            ))
    
    def create_attack_particles(self, target, particles):
        mid_x = (self.x + target.x) / 2
        mid_y = (self.y + target.y) / 2
        
        for _ in range(12):
            particles.append(Particle(
                mid_x,
                mid_y,
                random.uniform(-200, 200),
                random.uniform(-200, 200),
                Color(255, 255, 255),
                random.uniform(0.3, 1.0)
            ))
    
    def explode(self, particles):
        # Explosion spectaculaire
        explosion_count = 25
        if self.rage_time > 0:
            explosion_count = 40  # Plus de particules si en rage
            
        for _ in range(explosion_count):
            particles.append(Particle(
                self.x,
                self.y,
                random.uniform(-400, 400),
                random.uniform(-400, 400),
                self.color,
                random.uniform(1.5, 4.0)
            ))
    
    def draw(self, screen):
        # Effets visuels des bonus
        glow_multiplier = 1.0
        if self.speed_boost_time > 0:
            glow_multiplier = 2.0
        if self.rage_time > 0:
            glow_multiplier = 2.5
        
        # Lueur
        glow_size = int(self.radius * (1 + self.glow_intensity * 0.5) * glow_multiplier)
        glow_surf = pygame.Surface((glow_size * 4, glow_size * 4), pygame.SRCALPHA)
        
        glow_color = self.color
        if self.rage_time > 0:
            glow_color = Color(255, 100, 100)
        elif self.speed_boost_time > 0:
            glow_color = Color(255, 255, 100)
        
        glow_alpha = int(120 * self.glow_intensity * glow_multiplier)
        glow_surf.set_alpha(glow_alpha)
        glow_rgb = (
            max(0, min(255, glow_color.r)),
            max(0, min(255, glow_color.g)),
            max(0, min(255, glow_color.b))
        )
        pygame.draw.circle(glow_surf, glow_rgb, (glow_size * 2, glow_size * 2), glow_size * 2)
        screen.blit(glow_surf, (int(self.x - glow_size * 2), int(self.y - glow_size * 2)))
        
        # Corps principal
        main_color = (
            max(0, min(255, self.color.r)),
            max(0, min(255, self.color.g)),
            max(0, min(255, self.color.b))
        )
        pygame.draw.circle(screen, main_color, (int(self.x), int(self.y)), int(self.radius))
        
        # Bouclier
        if self.shield_strength > 0:
            shield_radius = int(self.radius + 8)
            pygame.draw.circle(screen, (100, 200, 255), (int(self.x), int(self.y)), shield_radius, 4)
        
        # Barre de vie
        if self.health < self.max_health:
            bar_width = int(self.radius * 2.2)
            bar_height = 5
            bar_x = int(self.x - bar_width // 2)
            bar_y = int(self.y - self.radius - 12)
            
            # Fond de la barre
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            
            # Barre de vie
            health_ratio = max(0, min(1, self.health / self.max_health))
            health_width = int(bar_width * health_ratio)
            health_color = (
                int(255 * (1 - health_ratio)),
                int(255 * health_ratio),
                0
            )
            pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))

class Disruption:
    def __init__(self, disruption_type, duration):
        self.type = disruption_type
        self.duration = duration
        self.start_time = time.time()
        
    def is_active(self):
        return time.time() - self.start_time < self.duration
    
    def apply_to_ball(self, ball):
        if not self.is_active():
            return
            
        if self.type == "gravity_flip":
            ball.vy += 300 * (1/60)  # Gravité inversée plus forte
        elif self.type == "magnetic_field":
            # Attraction vers le centre de l'arène
            center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200
            dx = center_x - ball.x
            dy = center_y - ball.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                force = 150 / (dist + 1)
                ball.vx += (dx / dist) * force * (1/60)
                ball.vy += (dy / dist) * force * (1/60)
        elif self.type == "speed_boost":
            ball.vx *= 1.03
            ball.vy *= 1.03
        elif self.type == "chaos":
            if random.random() < 0.06:
                ball.vx += random.uniform(-100, 100)
                ball.vy += random.uniform(-100, 100)
        elif self.type == "shape_morph":
            # Change la forme de l'arène pendant la perturbation
            pass

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🔥 ARENA COMBAT - TikTok Viral! 🔥")
        self.clock = pygame.time.Clock()
        
        self.balls = []
        self.particles = []
        self.disruptions = []
        self.bonuses = []
        self.arena = Arena()
        
        self.start_time = time.time()
        self.last_disruption = 0
        self.last_bonus_spawn = 0
        self.bg_color = Color(15, 15, 30)
        self.combat_intensity = 0
        self.shape_change_timer = 0
        
        # Polices pour le texte
        self.font = pygame.font.Font(None, 48)
        self.big_font = pygame.font.Font(None, 84)
        self.small_font = pygame.font.Font(None, 36)
        
        # Création des balles initiales
        self.spawn_initial_balls()
    
    def spawn_initial_balls(self):
        ball_types = list(BallType)
        arena_center_x = self.arena.center_x
        arena_center_y = self.arena.center_y + 200
        
        for _ in range(12):
            # Spawn dans l'arène
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(50, 200)
            x = arena_center_x + radius * math.cos(angle)
            y = arena_center_y + radius * math.sin(angle)
            
            ball_type = random.choice(ball_types)
            self.balls.append(Ball(x, y, ball_type))
    
    def spawn_bonus(self):
        # Spawn un bonus dans l'arène
        arena_center_x = self.arena.center_x
        arena_center_y = self.arena.center_y + 200
        
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(80, 250)
        x = arena_center_x + radius * math.cos(angle)
        y = arena_center_y + radius * math.sin(angle)
        
        bonus_types = list(BonusType)
        bonus_type = random.choice(bonus_types)
        self.bonuses.append(Bonus(x, y, bonus_type))
    
    def add_disruption(self):
        disruption_types = ["gravity_flip", "magnetic_field", "speed_boost", "chaos", "shape_morph"]
        disruption_type = random.choice(disruption_types)
        duration = random.uniform(4, 10)
        
        # Shape morph change la forme de l'arène
        if disruption_type == "shape_morph":
            shapes = ["hexagon", "octagon", "diamond"]
            current_shape = self.arena.shape_type
            new_shapes = [s for s in shapes if s != current_shape]
            self.arena.shape_type = random.choice(new_shapes)
            self.arena.generate_shape()
            duration = 15.0  # Plus long pour que ce soit visible
        
        self.disruptions.append(Disruption(disruption_type, duration))
        
        # Ajouter des balles supplémentaires parfois
        if random.random() < 0.4:
            for _ in range(random.randint(2, 4)):
                arena_center_x = self.arena.center_x
                arena_center_y = self.arena.center_y + 200
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(50, 180)
                x = arena_center_x + radius * math.cos(angle)
                y = arena_center_y + radius * math.sin(angle)
                
                ball_type = random.choice(list(BallType))
                self.balls.append(Ball(x, y, ball_type))
    
    def handle_bonus_effects(self):
        # Gérer les effets spéciaux des bonus collectés
        for ball in self.balls[:]:
            for bonus in self.bonuses[:]:
                if bonus.check_collision(ball):
                    if bonus.type == BonusType.MULTIPLY:
                        # Dupliquer la balle
                        new_ball = Ball(ball.x + 30, ball.y + 30, ball.type)
                        new_ball.vx = -ball.vx * 0.8
                        new_ball.vy = -ball.vy * 0.8
                        self.balls.append(new_ball)
                    
                    # Créer des particules d'effet
                    for _ in range(15):
                        self.particles.append(Particle(
                            bonus.x,
                            bonus.y,
                            random.uniform(-200, 200),
                            random.uniform(-200, 200),
                            bonus.color,
                            random.uniform(1.0, 2.0)
                        ))
                    
                    self.bonuses.remove(bonus)
    
    def update_background_intensity(self):
        # Calculer l'intensité basée sur le nombre de balles, particules et bonus
        ball_count = len(self.balls)
        particle_count = len(self.particles)
        bonus_count = len(self.bonuses)
        
        # Plus il y a d'action, plus l'intensité augmente
        self.combat_intensity = min(1.0, (ball_count * 2 + particle_count * 0.15 + bonus_count * 3) / 80)
        
        # Couleur de fond dynamique
        base_color = Color(15, 15, 30)
        intense_color = Color(80, 30, 60)  # Plus violet/rouge pour l'intensité
        self.bg_color = base_color.lerp(intense_color, self.combat_intensity)
    
    def draw_hud(self, elapsed_time):
        # Interface utilisateur améliorée
        remaining_time = max(0, GAME_DURATION - elapsed_time)
        
        # Temps restant avec style
        time_color = (255, 255, 255)
        if remaining_time < 10:
            time_color = (255, 100, 100)  # Rouge pour l'urgence
        elif remaining_time < 20:
            time_color = (255, 200, 100)  # Orange pour l'avertissement
            
        time_text = self.big_font.render(f"⏰ {remaining_time:.1f}s", True, time_color)
        self.screen.blit(time_text, (30, 30))
        
        # Statistiques du combat
        stats_y = 120
        ball_text = self.font.render(f"⚔️ Combattants: {len(self.balls)}", True, (255, 255, 255))
        self.screen.blit(ball_text, (30, stats_y))
        
        bonus_text = self.small_font.render(f"💎 Bonus actifs: {len(self.bonuses)}", True, (200, 200, 255))
        self.screen.blit(bonus_text, (30, stats_y + 50))
        
        # Indicateur d'intensité du combat
        intensity_bar_width = 200
        intensity_bar_height = 8
        intensity_x = 30
        intensity_y = stats_y + 90
        
        pygame.draw.rect(self.screen, (50, 50, 50), 
                        (intensity_x, intensity_y, intensity_bar_width, intensity_bar_height))
        
        intensity_fill = int(intensity_bar_width * self.combat_intensity)
        intensity_color = (
            int(255 * self.combat_intensity),
            int(255 * (1 - self.combat_intensity)),
            100
        )
        pygame.draw.rect(self.screen, intensity_color,
                        (intensity_x, intensity_y, intensity_fill, intensity_bar_height))
        
        intensity_label = self.small_font.render("🔥 INTENSITÉ", True, (255, 255, 255))
        self.screen.blit(intensity_label, (intensity_x, intensity_y - 25))
        
        # Indicateur de forme d'arène
        shape_name = self.arena.shape_type.upper()
        shape_text = self.small_font.render(f"🏟️ ARÈNE: {shape_name}", True, (150, 200, 255))
        self.screen.blit(shape_text, (30, stats_y + 130))
        
        # Indicateur de perturbation active
        if self.disruptions:
            disruption_names = {
                "gravity_flip": "🌀 GRAVITÉ INVERSÉE",
                "magnetic_field": "🧲 CHAMP MAGNÉTIQUE", 
                "speed_boost": "⚡ ACCÉLÉRATION",
                "chaos": "💥 CHAOS TOTAL",
                "shape_morph": "🔄 MORPHING ARÈNE"
            }
            
            for disruption in self.disruptions:
                name = disruption_names.get(disruption.type, disruption.type.upper())
                disruption_text = self.font.render(name, True, (255, 150, 150))
                text_rect = disruption_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
                
                # Effet de pulsation
                pulse = math.sin(time.time() * 8) * 0.1 + 0.9
                scaled_surface = pygame.transform.scale(disruption_text, 
                    (int(disruption_text.get_width() * pulse), 
                     int(disruption_text.get_height() * pulse)))
                
                scaled_rect = scaled_surface.get_rect(center=text_rect.center)
                self.screen.blit(scaled_surface, scaled_rect)
    
    def draw_legend(self):
        # Légende des types de balles
        legend_x = SCREEN_WIDTH - 280
        legend_y = 30
        
        legend_title = self.small_font.render("🎯 TYPES DE COMBATTANTS", True, (255, 255, 255))
        self.screen.blit(legend_title, (legend_x, legend_y))
        
        ball_info = {
            BallType.FIRE: "🔥 FEU - Chasse la glace",
            BallType.ICE: "❄️ GLACE - Ralentit",
            BallType.METAL: "⚙️ MÉTAL - Magnétisme",
            BallType.LIGHTNING: "⚡ FOUDRE - Erratique", 
            BallType.POISON: "☠️ POISON - Toxique"
        }
        
        y_offset = 60
        for ball_type, description in ball_info.items():
            color = COLORS[ball_type]
            
            # Petit cercle coloré
            pygame.draw.circle(self.screen, color.to_tuple(), 
                             (legend_x + 10, legend_y + y_offset + 8), 8)
            
            # Description
            desc_text = self.small_font.render(description, True, (200, 200, 200))
            self.screen.blit(desc_text, (legend_x + 30, legend_y + y_offset))
            
            y_offset += 35
        
        # Légende des bonus
        bonus_legend_y = legend_y + y_offset + 30
        bonus_title = self.small_font.render("💎 BONUS ÉPIQUES", True, (255, 255, 255))
        self.screen.blit(bonus_title, (legend_x, bonus_legend_y))
        
        bonus_info = {
            "💨 VITESSE": "Accélération +50%",
            "💚 SOIN": "Restaure la santé",
            "🛡️ BOUCLIER": "Protection 8s",
            "✖️ CLONAGE": "Duplique la balle",
            "😡 RAGE": "Dégâts x3",
            "❄️ FREEZE": "Gèle tout autour"
        }
        
        y_offset = 30
        for icon_desc, effect in bonus_info.items():
            bonus_text = self.small_font.render(f"{icon_desc}: {effect}", True, (150, 255, 150))
            self.screen.blit(bonus_text, (legend_x, bonus_legend_y + y_offset))
            y_offset += 25
    
    def run(self):
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            
            # Événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        # Changer la forme manuellement (pour le debug)
                        shapes = ["hexagon", "octagon", "diamond"]
                        current_idx = shapes.index(self.arena.shape_type)
                        self.arena.shape_type = shapes[(current_idx + 1) % len(shapes)]
                        self.arena.generate_shape()
            
            # Fin du jeu après 61 secondes
            if elapsed_time >= GAME_DURATION:
                self.final_explosion()
                pygame.time.wait(3000)
                running = False
                continue
            
            # Ajouter des perturbations
            if elapsed_time - self.last_disruption >= DISRUPTION_INTERVAL:
                self.add_disruption()
                self.last_disruption = elapsed_time
            
            # Spawn des bonus
            if elapsed_time - self.last_bonus_spawn >= BONUS_SPAWN_INTERVAL:
                self.spawn_bonus()
                self.last_bonus_spawn = elapsed_time
            
            # Mise à jour des bonus
            self.bonuses = [b for b in self.bonuses if b.update(dt)]
            self.handle_bonus_effects()
            
            # Mise à jour des balles
            dead_balls = []
            for ball in self.balls[:]:
                ball.update(dt, self.balls, self.particles, self.disruptions, self.arena)
                if ball.health <= 0:
                    ball.explode(self.particles)
                    dead_balls.append(ball)
            
            for ball in dead_balls:
                self.balls.remove(ball)
            
            # Mise à jour des particules
            self.particles = [p for p in self.particles if p.update(dt)]
            
            # Nettoyer les perturbations expirées
            self.disruptions = [d for d in self.disruptions if d.is_active()]
            
            # Mise à jour de l'intensité du fond
            self.update_background_intensity()
            
            # Rendu
            self.draw(elapsed_time)
        
        pygame.quit()
    
    def final_explosion(self):
        # Explosion finale ultra-spectaculaire
        for ball in self.balls:
            for _ in range(50):  # Plus de particules
                self.particles.append(Particle(
                    ball.x,
                    ball.y,
                    random.uniform(-800, 800),
                    random.uniform(-800, 800),
                    ball.color,
                    random.uniform(3.0, 8.0)  # Durée plus longue
                ))
        
        # Explosion des bonus restants
        for bonus in self.bonuses:
            for _ in range(20):
                self.particles.append(Particle(
                    bonus.x,
                    bonus.y,
                    random.uniform(-500, 500),
                    random.uniform(-500, 500),
                    bonus.color,
                    random.uniform(2.0, 5.0)
                ))
        
        # Effet de flash white plus long
        for alpha in [255, 200, 150, 100, 50]:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surf.fill((255, 255, 255))
            flash_surf.set_alpha(alpha)
            
            # Dessiner le frame avec le flash
            self.draw_background()
            self.arena.draw(self.screen)
            
            for particle in self.particles:
                particle.draw(self.screen)
                
            self.screen.blit(flash_surf, (0, 0))
            
            # Texte final
            final_text = self.big_font.render("💥 EXPLOSION FINALE! 💥", True, (255, 0, 0))
            text_rect = final_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(final_text, text_rect)
            
            pygame.display.flip()
            pygame.time.wait(200)
        
        self.balls.clear()
        self.bonuses.clear()
    
    def draw_background(self):
        # Fond dégradé amélioré
        for y in range(0, SCREEN_HEIGHT, 3):  # Optimisation
            gradient_factor = y / SCREEN_HEIGHT
            
            # Effet de vague basé sur le temps
            wave_effect = math.sin(time.time() * 2 + y * 0.01) * 0.1
            
            color_r = max(0, min(255, int(self.bg_color.r * (1 - gradient_factor * 0.4 + wave_effect))))
            color_g = max(0, min(255, int(self.bg_color.g * (1 - gradient_factor * 0.3 + wave_effect))))
            color_b = max(0, min(255, int(self.bg_color.b * (1 + gradient_factor * 0.6 + wave_effect))))
            
            pygame.draw.rect(self.screen, (color_r, color_g, color_b), (0, y, SCREEN_WIDTH, 3))
    
    def draw(self, elapsed_time):
        # Fond dégradé avec effet
        self.draw_background()
        
        # Arène (dessiner en premier pour qu'elle soit derrière)
        self.arena.draw(self.screen)
        
        # Particules
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Bonus
        for bonus in self.bonuses:
            bonus.draw(self.screen)
        
        # Balles (par-dessus tout)
        for ball in self.balls:
            ball.draw(self.screen)
        
        # Interface utilisateur
        self.draw_hud(elapsed_time)
        self.draw_legend()
        
        # Effet de fin de jeu
        remaining_time = max(0, GAME_DURATION - elapsed_time)
        if remaining_time < 10:
            warning_size = int(84 + math.sin(elapsed_time * 15) * 30)
            warning_font = pygame.font.Font(None, warning_size)
            
            if remaining_time < 5:
                warning_text = warning_font.render("🚨 EXPLOSION IMMINENTE! 🚨", True, (255, 100, 100))
                shadow_text = warning_font.render("🚨 EXPLOSION IMMINENTE! 🚨", True, (100, 0, 0))
            else:
                warning_text = warning_font.render("⚠️ ATTENTION! ⚠️", True, (255, 200, 100))
                shadow_text = warning_font.render("⚠️ ATTENTION! ⚠️", True, (100, 50, 0))
                
            text_rect = warning_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200))
            
            # Effet d'ombre
            shadow_rect = shadow_text.get_rect(center=(text_rect.centerx + 3, text_rect.centery + 3))
            self.screen.blit(shadow_text, shadow_rect)
            self.screen.blit(warning_text, text_rect)
        
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
