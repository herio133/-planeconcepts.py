import pygame
import sys
import math
import random
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 900, 600
FPS = 60
GRID_SIZE = 25

# Colors (elegant dark theme)
DARK_BG = (15, 15, 25)
GRID_COLOR = (40, 40, 60)
AXIS_COLOR = (80, 80, 120)
EUCLIDEAN_COLOR = (100, 200, 255)
AFFINE_COLOR = (255, 150, 100)
POINT_COLOR = (255, 255, 100)
TEXT_COLOR = (200, 200, 220)
HIGHLIGHT_COLOR = (255, 255, 255)
PARALLEL_COLOR = (150, 255, 150)

class GeometryMode(Enum):
    EUCLIDEAN = 1
    AFFINE = 2
    BOTH = 3

class GeometryViz:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Geometry: Euclidean & Affine Planes")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        
        # Geometry state
        self.mode = GeometryMode.BOTH
        self.show_grid = True
        self.animate = True
        self.time = 0
        
        # Points (in mathematical coordinates)
        self.points = {
            'A': [-120, -80],
            'B': [150, 120],
            'C': [-80, 150],
            'D': [120, -120]
        }
        
        # Dragging state
        self.dragging = None
        self.drag_offset = [0, 0]
        
        # Animation parameters
        self.pulse_phase = 0
        self.rotation_angle = 0
        
        # Parallel lines for affine demonstration
        self.parallel_lines = []
        self.generate_parallel_lines()
    
    def generate_parallel_lines(self):
        """Generate parallel lines to demonstrate affine properties"""
        self.parallel_lines = []
        for i in range(3):
            # Create parallel lines with same direction vector
            offset = i * 45 - 45
            self.parallel_lines.append({
                'start': [-250, -150 + offset],
                'end': [250, 150 + offset],
                'offset': offset
            })
    
    def to_screen(self, x, y):
        """Convert mathematical coordinates to screen coordinates"""
        return int(WIDTH / 2 + x), int(HEIGHT / 2 - y)
    
    def to_math(self, screen_x, screen_y):
        """Convert screen coordinates to mathematical coordinates"""
        return screen_x - WIDTH // 2, HEIGHT // 2 - screen_y
    
    def draw_elegant_grid(self):
        """Draw an elegant grid system"""
        if not self.show_grid:
            return
            
        # Draw subtle grid lines
        for x in range(-WIDTH//2, WIDTH//2, GRID_SIZE):
            screen_x = WIDTH//2 + x
            alpha = max(30, 60 - abs(x) // 10)
            color = (*GRID_COLOR[:2], min(255, alpha))
            pygame.draw.line(self.screen, GRID_COLOR, (screen_x, 0), (screen_x, HEIGHT), 1)
        
        for y in range(-HEIGHT//2, HEIGHT//2, GRID_SIZE):
            screen_y = HEIGHT//2 - y
            pygame.draw.line(self.screen, GRID_COLOR, (0, screen_y), (WIDTH, screen_y), 1)
    
    def draw_axes(self):
        """Draw coordinate axes with elegant styling"""
        # Main axes
        pygame.draw.line(self.screen, AXIS_COLOR, (0, HEIGHT//2), (WIDTH, HEIGHT//2), 2)
        pygame.draw.line(self.screen, AXIS_COLOR, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)
        
        # Axis arrows
        arrow_size = 10
        # X-axis arrow
        pygame.draw.polygon(self.screen, AXIS_COLOR, [
            (WIDTH - 15, HEIGHT//2),
            (WIDTH - 15 - arrow_size, HEIGHT//2 - 5),
            (WIDTH - 15 - arrow_size, HEIGHT//2 + 5)
        ])
        # Y-axis arrow
        pygame.draw.polygon(self.screen, AXIS_COLOR, [
            (WIDTH//2, 15),
            (WIDTH//2 - 5, 15 + arrow_size),
            (WIDTH//2 + 5, 15 + arrow_size)
        ])
        
        # Axis labels
        x_label = self.font.render("x", True, TEXT_COLOR)
        y_label = self.font.render("y", True, TEXT_COLOR)
        self.screen.blit(x_label, (WIDTH - 30, HEIGHT//2 + 10))
        self.screen.blit(y_label, (WIDTH//2 + 10, 20))
    
    def draw_euclidean_elements(self):
        """Draw Euclidean geometry elements with elegant effects"""
        if self.mode == GeometryMode.AFFINE:
            return
            
        A, B = self.points['A'], self.points['B']
        C, D = self.points['C'], self.points['D']
        
        # Animated line thickness
        base_thickness = 3
        pulse = math.sin(self.pulse_phase) * 0.5 + 1
        thickness = int(base_thickness * pulse)
        
        # Draw main line AB with glow effect
        for i in range(5, 0, -1):
            alpha = (6 - i) * 30
            color = (*EUCLIDEAN_COLOR, min(255, alpha))
            pygame.draw.line(self.screen, EUCLIDEAN_COLOR, 
                           self.to_screen(*A), self.to_screen(*B), thickness + i)
        
        # Draw perpendicular line through midpoint (Euclidean property)
        mid_x = (A[0] + B[0]) / 2
        mid_y = (A[1] + B[1]) / 2
        
        # Calculate perpendicular direction
        dx, dy = B[0] - A[0], B[1] - A[1]
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            perp_dx, perp_dy = -dy/length * 80, dx/length * 80
            perp_start = [mid_x + perp_dx, mid_y + perp_dy]
            perp_end = [mid_x - perp_dx, mid_y - perp_dy]
            
            pygame.draw.line(self.screen, EUCLIDEAN_COLOR, 
                           self.to_screen(*perp_start), self.to_screen(*perp_end), 2)
        
        # Draw distance measurement (Euclidean concept)
        distance = math.sqrt((B[0] - A[0])**2 + (B[1] - A[1])**2)
        dist_text = self.font.render(f"d(A,B) = {distance:.1f}", True, EUCLIDEAN_COLOR)
        self.screen.blit(dist_text, (50, 50))
    
    def draw_affine_elements(self):
        """Draw Affine geometry elements"""
        if self.mode == GeometryMode.EUCLIDEAN:
            return
            
        # Draw parallel lines (key affine property)
        for i, line in enumerate(self.parallel_lines):
            alpha = 150 + int(50 * math.sin(self.time + i))
            color = (*PARALLEL_COLOR, min(255, alpha))
            
            start_screen = self.to_screen(*line['start'])
            end_screen = self.to_screen(*line['end'])
            pygame.draw.line(self.screen, PARALLEL_COLOR, start_screen, end_screen, 2)
        
        # Draw affine transformation demonstration
        A, B, C = self.points['A'], self.points['B'], self.points['C']
        
        # Original triangle
        triangle_points = [self.to_screen(*A), self.to_screen(*B), self.to_screen(*C)]
        pygame.draw.polygon(self.screen, AFFINE_COLOR, triangle_points, 2)
        
        # Transformed triangle (shear transformation)
        shear_factor = 0.3 * math.sin(self.time * 0.5)
        transformed = []
        for point in [A, B, C]:
            tx = point[0] + shear_factor * point[1]
            ty = point[1]
            transformed.append(self.to_screen(tx, ty))
        
        pygame.draw.polygon(self.screen, AFFINE_COLOR, transformed, 2)
        
        # Show affine properties text
        affine_text = self.font.render("Affine Properties: Parallel lines remain parallel", True, AFFINE_COLOR)
        self.screen.blit(affine_text, (30, HEIGHT - 80))
        
        ratio_text = self.font.render("Ratios of parallel segments preserved", True, AFFINE_COLOR)
        self.screen.blit(ratio_text, (30, HEIGHT - 55))
    
    def draw_points(self):
        """Draw interactive points with elegant styling"""
        for name, pos in self.points.items():
            screen_pos = self.to_screen(*pos)
            
            # Animated point size
            base_size = 8
            if self.dragging == name:
                pulse = math.sin(self.pulse_phase * 2) * 2 + 6
                size = int(base_size + pulse)
            else:
                size = base_size
            
            # Draw point with glow
            for i in range(3, 0, -1):
                alpha = (4 - i) * 60
                pygame.draw.circle(self.screen, POINT_COLOR, screen_pos, size + i)
            
            # Point label
            label = self.font.render(name, True, TEXT_COLOR)
            label_pos = (screen_pos[0] + 12, screen_pos[1] - 12)
            self.screen.blit(label, label_pos)
            
            # Show coordinates
            coord_text = f"({pos[0]:.0f}, {pos[1]:.0f})"
            coord_label = self.font.render(coord_text, True, TEXT_COLOR)
            coord_pos = (screen_pos[0] + 12, screen_pos[1] + 5)
            self.screen.blit(coord_label, coord_pos)
    
    def draw_ui(self):
        """Draw elegant UI elements"""
        # Title
        title = self.title_font.render("Euclidean & Affine Planes", True, HIGHLIGHT_COLOR)
        self.screen.blit(title, (20, 20))
        
        # Mode indicator
        mode_text = f"Mode: {self.mode.name}"
        mode_label = self.font.render(mode_text, True, TEXT_COLOR)
        self.screen.blit(mode_label, (20, 70))
        
        # Instructions (smaller font and repositioned)
        small_font = pygame.font.Font(None, 18)
        instructions = [
            "Keys: E=Euclidean, A=Affine, B=Both",
            "G=Grid, Space=Animate, R=Reset",
            "Drag points to explore properties"
        ]
        
        for i, instruction in enumerate(instructions):
            text = small_font.render(instruction, True, TEXT_COLOR)
            self.screen.blit(text, (WIDTH - 280, 30 + i * 20))
    
    def handle_mouse(self, mouse_pos, mouse_pressed):
        """Handle mouse interactions"""
        if mouse_pressed[0]:  # Left mouse button
            if self.dragging is None:
                # Check if clicking on a point
                for name, pos in self.points.items():
                    screen_pos = self.to_screen(*pos)
                    distance = math.sqrt((mouse_pos[0] - screen_pos[0])**2 + 
                                       (mouse_pos[1] - screen_pos[1])**2)
                    if distance < 15:
                        self.dragging = name
                        self.drag_offset = [mouse_pos[0] - screen_pos[0], 
                                          mouse_pos[1] - screen_pos[1]]
                        break
            else:
                # Update dragged point position
                new_pos = self.to_math(mouse_pos[0] - self.drag_offset[0], 
                                     mouse_pos[1] - self.drag_offset[1])
                self.points[self.dragging] = list(new_pos)
        else:
            self.dragging = None
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.time += dt
            
            if self.animate:
                self.pulse_phase += dt * 3
                self.rotation_angle += dt * 0.5
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        self.mode = GeometryMode.EUCLIDEAN
                    elif event.key == pygame.K_a:
                        self.mode = GeometryMode.AFFINE
                    elif event.key == pygame.K_b:
                        self.mode = GeometryMode.BOTH
                    elif event.key == pygame.K_g:
                        self.show_grid = not self.show_grid
                    elif event.key == pygame.K_SPACE:
                        self.animate = not self.animate
                    elif event.key == pygame.K_r:
                        # Reset points to default positions
                        self.points = {
                            'A': [-120, -80],
                            'B': [150, 120],
                            'C': [-80, 150],
                            'D': [120, -120]
                        }
            
            # Handle mouse
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            self.handle_mouse(mouse_pos, mouse_pressed)
            
            # Draw everything
            self.screen.fill(DARK_BG)
            self.draw_elegant_grid()
            self.draw_axes()
            self.draw_euclidean_elements()
            self.draw_affine_elements()
            self.draw_points()
            self.draw_ui()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

# Run the visualization
if __name__ == "__main__":
    viz = GeometryViz()
    viz.run()
