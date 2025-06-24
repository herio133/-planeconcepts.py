'''ℝ² confusion
Convenient: We have 2D screens, paper, blackboards
Intuitive: Our visual system evolved for 3D space, so 2D projections feel natural
Historical: Centuries of mathematical tradition using Cartesian coordinates'''

import pygame
import sys
import math
import numpy as np
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 800
FPS = 60
GRID_SIZE = 25

# Colors
DARK_BG = (8, 12, 20)
GRID_COLOR = (30, 35, 50)
AXIS_COLOR = (60, 70, 100)
REAL_SECTION_COLOR = (100, 200, 255)      # What we see in ℝ²
COMPLEX_HIDDEN_COLOR = (255, 100, 150)    # What's hidden in complex directions
PROJECTION_COLOR = (255, 255, 100)        # Projection lines
CROSS_SECTION_COLOR = (150, 255, 150)     # Cross-section indicator
TEXT_COLOR = (200, 200, 220)
HIGHLIGHT_COLOR = (255, 255, 255)
DIM_COLOR = (100, 100, 120)

class ViewMode(Enum):
    REAL_PLANE = "Real Plane ℝ²"
    COMPLEX_PROJECTION = "ℂ² → ℝ² Projection"
    FOUR_D_SLICES = "ℝ⁴ Cross-Sections" 
    MULTI_FIELD = "Different Fields k"

class CrossSectionViz:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Cross-Sections of Higher-Dimensional Algebraic Spaces")
        self.clock = pygame.time.Clock()
        
        # Initialize fonts with fallback
        try:
            self.font = pygame.font.Font(None, 20)
            self.title_font = pygame.font.Font(None, 28)
            self.math_font = pygame.font.Font(None, 16)
            self.small_font = pygame.font.Font(None, 14)
        except:
            self.font = pygame.font.SysFont('arial', 16)
            self.title_font = pygame.font.SysFont('arial', 22)
            self.math_font = pygame.font.SysFont('arial', 12)
            self.small_font = pygame.font.SysFont('arial', 10)
        
        # State
        self.view_mode = ViewMode.REAL_PLANE
        self.time = 0
        self.show_projections = True
        self.show_hidden_dims = True
        self.animate = True
        
        # Cross-section parameters
        self.slice_real_im = 0.0      # Im(z₁) = constant
        self.slice_imaginary = 0.0    # Im(z₂) = constant
        self.viewing_angle = 0.0      # Rotation in 4D space
        
        # Curve equation: z₁² + z₂² = r² over ℂ
        self.radius = 80
        
    def to_screen(self, x, y, offset_x=0, offset_y=0):
        """Convert coordinates to screen with optional offset"""
        base_x = WIDTH // 2 + offset_x
        base_y = HEIGHT // 2 + offset_y
        return int(base_x + x), int(base_y - y)
    
    def complex_circle_solutions(self, r):
        """Generate solutions to z₁² + z₂² = r² over ℂ"""
        solutions = []
        
        # Parametric: z₁ = r*cos(t), z₂ = r*sin(t) where t can be complex
        for real_t in np.linspace(0, 2*math.pi, 40):
            for complex_param in np.linspace(-0.5, 0.5, 5):  # Small imaginary part
                t = complex(real_t, complex_param)
                
                # z₁ = r * cos(t), z₂ = r * sin(t)
                z1 = r * complex(math.cos(t.real) * math.cosh(t.imag), 
                                -math.sin(t.real) * math.sinh(t.imag))
                z2 = r * complex(math.sin(t.real) * math.cosh(t.imag), 
                                math.cos(t.real) * math.sinh(t.imag))
                
                solutions.append((z1, z2))
        
        return solutions
    
    def draw_coordinate_system(self, offset_x=0, offset_y=0, label=""):
        """Draw coordinate system with given offset"""
        center_x = WIDTH // 2 + offset_x
        center_y = HEIGHT // 2 + offset_y
        
        # Grid
        for i in range(-5, 6):
            x = center_x + i * GRID_SIZE
            y = center_y + i * GRID_SIZE
            if 0 <= x <= WIDTH:
                pygame.draw.line(self.screen, GRID_COLOR, (x, center_y - 150), (x, center_y + 150), 1)
            if 0 <= y <= HEIGHT:
                pygame.draw.line(self.screen, GRID_COLOR, (center_x - 150, y), (center_x + 150, y), 1)
        
        # Axes
        pygame.draw.line(self.screen, AXIS_COLOR, 
                        (center_x - 150, center_y), (center_x + 150, center_y), 2)
        pygame.draw.line(self.screen, AXIS_COLOR, 
                        (center_x, center_y - 150), (center_x, center_y + 150), 2)
        
        # Label
        if label:
            label_surface = self.font.render(label, True, HIGHLIGHT_COLOR)
            self.screen.blit(label_surface, (center_x - 100, center_y - 180))
    
    def draw_real_plane_view(self):
        """Show what we normally see: just the real part"""
        self.draw_coordinate_system(0, 0, "Standard ℝ² View")
        
        # Draw real circle: x² + y² = r²
        center = self.to_screen(0, 0)
        pygame.draw.circle(self.screen, REAL_SECTION_COLOR, center, self.radius, 3)
        
        # Annotations
        annotations = [
            "What we usually see:",
            "Real solutions to x² + y² = r²",
            "Just the 'tip of the iceberg'!",
            "",
            "Missing: All complex solutions",
            "where x, y ∈ ℂ instead of ℝ"
        ]
        
        for i, text in enumerate(annotations):
            color = HIGHLIGHT_COLOR if i == 0 else TEXT_COLOR
            surface = self.math_font.render(text, True, color)
            self.screen.blit(surface, (50, 100 + i * 18))
    
    def draw_complex_projection_view(self):
        """Show projection from ℂ² to ℝ²"""
        # Left side: Full ℂ² space representation
        self.draw_coordinate_system(-200, 0, "Re(z₁) × Re(z₂)")
        
        # Right side: Projection result  
        self.draw_coordinate_system(200, 0, "Projected View")
        
        # Get complex solutions
        solutions = self.complex_circle_solutions(self.radius)
        
        # Draw the projection process
        for i, (z1, z2) in enumerate(solutions[::3]):  # Subsample for clarity
            # Full complex point (show real parts)
            real_pt = self.to_screen(z1.real, z2.real, -200, 0)
            
            # Projected point (same as real part)
            proj_pt = self.to_screen(z1.real, z2.real, 200, 0)
            
            # Draw points
            pygame.draw.circle(self.screen, COMPLEX_HIDDEN_COLOR, real_pt, 2)
            pygame.draw.circle(self.screen, REAL_SECTION_COLOR, proj_pt, 2)
            
            # Draw projection line
            if self.show_projections and i % 5 == 0:
                pygame.draw.line(self.screen, PROJECTION_COLOR, real_pt, proj_pt, 1)
        
        # Show what's hidden
        hidden_info = [
            "ℂ² ≅ ℝ⁴ has MUCH more structure:",
            "• Each point (z₁, z₂) has 4 real coordinates",
            "• z₁ = x₁ + iy₁, z₂ = x₂ + iy₂", 
            "• We only see (x₁, x₂) projection!",
            "",
            "Hidden: (y₁, y₂) components",
            "These contain most of the solutions!"
        ]
        
        for i, text in enumerate(hidden_info):
            color = HIGHLIGHT_COLOR if "ℂ²" in text else TEXT_COLOR
            surface = self.math_font.render(text, True, color)
            self.screen.blit(surface, (50, HEIGHT - 200 + i * 16))
    
    def draw_four_d_slices(self):
        """Show different slices through ℝ⁴"""
        # Four quadrants showing different 2D slices of ℝ⁴
        positions = [(-250, -150), (250, -150), (-250, 150), (250, 150)]
        labels = [
            f"Re(z₁) × Re(z₂), Im=({self.slice_real_im:.1f},{self.slice_imaginary:.1f})",
            f"Re(z₁) × Im(z₁), Re(z₂)=0, Im(z₂)={self.slice_imaginary:.1f}",
            f"Re(z₂) × Im(z₂), Re(z₁)=0, Im(z₁)={self.slice_real_im:.1f}", 
            f"Im(z₁) × Im(z₂), Re=({self.slice_real_im:.1f},{self.slice_imaginary:.1f})"
        ]
        
        for i, (offset_x, offset_y) in enumerate(positions):
            self.draw_coordinate_system(offset_x, offset_y, labels[i])
            
            # Draw cross-section through 4D space
            if i == 0:  # Standard real view
                center = self.to_screen(0, 0, offset_x, offset_y)
                pygame.draw.circle(self.screen, REAL_SECTION_COLOR, center, 50, 2)
            
            elif i == 1:  # Re(z₁) × Im(z₁) slice
                # This shows hyperbolic sections for complex solutions
                for x in np.linspace(-50, 50, 100):
                    # From z₁² + z₂² = r², if z₂ is fixed, z₁ traces hyperbola
                    try:
                        y_val = math.sqrt(abs(self.radius**2 - self.slice_imaginary**2 - x**2))
                        pt1 = self.to_screen(x, y_val, offset_x, offset_y)
                        pt2 = self.to_screen(x, -y_val, offset_x, offset_y)
                        pygame.draw.circle(self.screen, COMPLEX_HIDDEN_COLOR, pt1, 1)
                        pygame.draw.circle(self.screen, COMPLEX_HIDDEN_COLOR, pt2, 1)
                    except:
                        pass
            
            elif i == 2:  # Re(z₂) × Im(z₂) slice  
                for x in np.linspace(-50, 50, 100):
                    try:
                        y_val = math.sqrt(abs(self.radius**2 - self.slice_real_im**2 - x**2))
                        pt1 = self.to_screen(x, y_val, offset_x, offset_y)
                        pt2 = self.to_screen(x, -y_val, offset_x, offset_y)
                        pygame.draw.circle(self.screen, COMPLEX_HIDDEN_COLOR, pt1, 1)
                        pygame.draw.circle(self.screen, COMPLEX_HIDDEN_COLOR, pt2, 1)
                    except:
                        pass
            
            elif i == 3:  # Im(z₁) × Im(z₂) slice
                # Pure imaginary slice
                center = self.to_screen(0, 0, offset_x, offset_y)
                radius_adjusted = max(10, self.radius - abs(self.slice_real_im + self.slice_imaginary))
                pygame.draw.circle(self.screen, COMPLEX_HIDDEN_COLOR, center, 
                                 int(radius_adjusted), 2)
        
        # Slice control info
        slice_info = [
            "4D Cross-Sections of A²(ℂ) ≅ ℝ⁴:",
            "Move slices with ↑↓←→ keys",
            f"Current slice parameters:",
            f"Im(z₁) = {self.slice_real_im:.2f}",
            f"Im(z₂) = {self.slice_imaginary:.2f}",
            "",
            "Each 2D view shows different",
            "cross-section of the 4D solution set!"
        ]
        
        for i, text in enumerate(slice_info):
            color = HIGHLIGHT_COLOR if "4D" in text else TEXT_COLOR
            surface = self.math_font.render(text, True, color)
            self.screen.blit(surface, (50, 50 + i * 16))
    
    def draw_multi_field_comparison(self):
        """Show how different fields give different 'planes'"""
        fields = ["ℝ", "ℂ", "𝔽₁₁", "ℚ̄"]
        positions = [(-250, -150), (250, -150), (-250, 150), (250, 150)]
        
        for i, (field, (offset_x, offset_y)) in enumerate(zip(fields, positions)):
            self.draw_coordinate_system(offset_x, offset_y, f"A²({field})")
            
            center = self.to_screen(0, 0, offset_x, offset_y)
            
            if field == "ℝ":
                # Real circle
                pygame.draw.circle(self.screen, REAL_SECTION_COLOR, center, 40, 2)
            
            elif field == "ℂ":
                # Complex "circle" - much richer structure
                pygame.draw.circle(self.screen, COMPLEX_HIDDEN_COLOR, center, 40, 2)
                pygame.draw.circle(self.screen, COMPLEX_HIDDEN_COLOR, center, 30, 1)
                pygame.draw.circle(self.screen, COMPLEX_HIDDEN_COLOR, center, 50, 1)
            
            elif field == "𝔽₁₁":
                # Finite field - discrete points
                for x in range(-2, 3):
                    for y in range(-2, 3):
                        if (x*x + y*y) % 11 == (self.radius//10) % 11:  # Simulate finite field arithmetic
                            pt = self.to_screen(x*15, y*15, offset_x, offset_y)
                            pygame.draw.circle(self.screen, (200, 100, 255), pt, 3)
            
            elif field == "ℚ̄":
                # Algebraic closure of rationals - very abstract
                # Show some rational approximations
                for angle in np.linspace(0, 2*math.pi, 20):
                    # Use rational approximations to show discrete nature
                    x = int(40 * math.cos(angle))
                    y = int(40 * math.sin(angle))
                    pt = self.to_screen(x, y, offset_x, offset_y)
                    pygame.draw.circle(self.screen, (255, 200, 100), pt, 2)
        
        # Field comparison info
        comparison_info = [
            "Same equation x² + y² = r² over different fields:",
            "",
            "ℝ: Standard real circle (1-dimensional)",
            "ℂ: Complex 'circle' (2-dimensional over ℝ)", 
            "𝔽₁₁: Discrete finite points",
            "ℚ̄: Algebraic numbers (dense but countable)",
            "",
            "The 'plane' visualization is only accurate for ℝ!",
            "For other fields, it's a convenient fiction."
        ]
        
        for i, text in enumerate(comparison_info):
            color = HIGHLIGHT_COLOR if text.startswith("Same equation") else TEXT_COLOR
            surface = self.math_font.render(text, True, color)
            self.screen.blit(surface, (50, 50 + i * 16))
    
    def draw_ui(self):
        """Draw user interface"""
        # Title
        title = f"Cross-Sections & Projections: {self.view_mode.value}"
        title_surface = self.title_font.render(title, True, HIGHLIGHT_COLOR)
        self.screen.blit(title_surface, (20, 20))
        
        # Controls
        controls = [
            "Controls: 1-4 = View modes, ↑↓←→ = Slice parameters",
            "P = Toggle projections, H = Toggle hidden dims, A = Animate"
        ]
        
        for i, control in enumerate(controls):
            surface = self.small_font.render(control, True, TEXT_COLOR)
            self.screen.blit(surface, (20, HEIGHT - 40 + i * 15))
    
    def run(self):
        """Main loop"""
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.time += dt
            
            if self.animate:
                self.slice_real_im = 0.3 * math.sin(self.time * 0.5)
                self.slice_imaginary = 0.3 * math.cos(self.time * 0.7)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.view_mode = ViewMode.REAL_PLANE
                    elif event.key == pygame.K_2:
                        self.view_mode = ViewMode.COMPLEX_PROJECTION
                    elif event.key == pygame.K_3:
                        self.view_mode = ViewMode.FOUR_D_SLICES
                    elif event.key == pygame.K_4:
                        self.view_mode = ViewMode.MULTI_FIELD
                    elif event.key == pygame.K_UP:
                        self.slice_real_im += 0.1
                    elif event.key == pygame.K_DOWN:
                        self.slice_real_im -= 0.1
                    elif event.key == pygame.K_LEFT:
                        self.slice_imaginary -= 0.1
                    elif event.key == pygame.K_RIGHT:
                        self.slice_imaginary += 0.1
                    elif event.key == pygame.K_p:
                        self.show_projections = not self.show_projections
                    elif event.key == pygame.K_h:
                        self.show_hidden_dims = not self.show_hidden_dims
                    elif event.key == pygame.K_a:
                        self.animate = not self.animate
            
            # Draw
            self.screen.fill(DARK_BG)
            
            if self.view_mode == ViewMode.REAL_PLANE:
                self.draw_real_plane_view()
            elif self.view_mode == ViewMode.COMPLEX_PROJECTION:
                self.draw_complex_projection_view()
            elif self.view_mode == ViewMode.FOUR_D_SLICES:
                self.draw_four_d_slices()
            elif self.view_mode == ViewMode.MULTI_FIELD:
                self.draw_multi_field_comparison()
            
            self.draw_ui()
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

# Run
if __name__ == "__main__":
    viz = CrossSectionViz()
    viz.run()

'''For arbitrary algebraically closed fields k (like ℚ̄, finite field closures, etc.):

No natural embedding into ℝ²
Completely wrong intuition about "distance," "angles," "continuity"
Topology doesn't exist in the usual sense'''
