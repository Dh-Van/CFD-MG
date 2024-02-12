import pygame
import pygame_gui
import random
import numpy as np

# Define some constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PIPE_WIDTH, PIPE_HEIGHT = 100, SCREEN_HEIGHT
PIPE_COLOR = (255, 255, 255)  # White
BACKGROUND_COLOR = (0, 0, 0)  # Black
WATER_COLOR = (0, 191, 255)  # Light blue
MOLECULE_SIZE = 5  # Decrease the size of the molecules to pack them closer together

# Define the water molecule class
class WaterMolecule(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((MOLECULE_SIZE, MOLECULE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WATER_COLOR, (MOLECULE_SIZE // 2, MOLECULE_SIZE // 2), MOLECULE_SIZE // 2)
        self.rect = self.image.get_rect()
        self.rect.x = x + random.uniform(-1, 1) * MOLECULE_SIZE
        self.rect.y = y + random.uniform(-1, 1) * MOLECULE_SIZE
        self.speed = np.array([0.0, 0.0])

    def update(self, pressure_force, viscosity, gravity):
        self.speed[1] += pressure_force + gravity  # Apply pressure force and gravity
        self.speed *= viscosity  # Apply viscosity
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]

        # Keep the molecule within the pipe
        if self.rect.x < SCREEN_WIDTH / 2 - PIPE_WIDTH / 2:
            self.rect.x = SCREEN_WIDTH / 2 - PIPE_WIDTH / 2
        elif self.rect.x > SCREEN_WIDTH / 2 + PIPE_WIDTH / 2 - self.rect.width:
            self.rect.x = SCREEN_WIDTH / 2 + PIPE_WIDTH / 2 - self.rect.width

        # Remove the molecule if it reaches the bottom of the screen
        if self.rect.y > SCREEN_HEIGHT:
            self.kill()

# Initialize Pygame and create a window
pygame.init()
pygame.display.set_caption('Water Simulation')
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create a group to hold the water molecules
water_molecules = pygame.sprite.Group()

# Create a clock to control the frame rate
clock = pygame.time.Clock()

# Create a GUI manager
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

# Initialize the slider variables
PRESSURE_FORCE = 0.1
VISCOSITY = 0.99
GRAVITY = 0.1  # Initialize the gravity variable

# Initialize the target and current values for the parameters
target_pressure_force = current_pressure_force = PRESSURE_FORCE
target_viscosity = current_viscosity = VISCOSITY
target_gravity = current_gravity = GRAVITY

# Create sliders for pressure force, viscosity and gravity
pressure_force_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, 70), (200, 20)),
                                                               start_value=PRESSURE_FORCE,
                                                               value_range=(0.0, 1.0),
                                                               manager=manager)
viscosity_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, 120), (200, 20)),
                                                          start_value=VISCOSITY,
                                                          value_range=(0.9, 1.0),
                                                          manager=manager)
gravity_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, 170), (200, 20)),
                                                        start_value=GRAVITY,
                                                        value_range=(0.0, 1.0),
                                                        manager=manager)  # Create a slider for gravity

# Create labels for the sliders
pressure_force_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, 50), (200, 20)),
                                                   text='Pressure Force',
                                                   manager=manager)
viscosity_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, 100), (200, 20)),
                                              text='Viscosity',
                                              manager=manager)
gravity_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, 150), (200, 20)),
                                            text='Gravity',
                                            manager=manager)  # Create a label for gravity

# Run the game loop
running = True
while running:
    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == pressure_force_slider:
                    target_pressure_force = event.value
                elif event.ui_element == viscosity_slider:
                    target_viscosity = event.value
                elif event.ui_element == gravity_slider:
                    target_gravity = event.value

        manager.process_events(event)

    # Gradually move the current values towards the target values
    current_pressure_force += (target_pressure_force - current_pressure_force) * 0.1
    current_viscosity += (target_viscosity - current_viscosity) * 0.1
    current_gravity += (target_gravity - current_gravity) * 0.1

    # Calculate the rate at which new molecules should be created
    creation_rate = 20 * (current_gravity + current_pressure_force) / (2 * current_viscosity)

    # Limit the creation rate to a reasonable range
    creation_rate = min(max(int(creation_rate * 10), 1), 10)

    # Add new water molecules at the top of the pipe
    for _ in range(creation_rate):  # Add molecules based on the creation rate
        if len(water_molecules) < 5000:  # Increase the limit of molecules
            x = random.uniform(SCREEN_WIDTH / 2 - PIPE_WIDTH / 2, SCREEN_WIDTH / 2 + PIPE_WIDTH / 2)
            water_molecule = WaterMolecule(x, 0)
            water_molecules.add(water_molecule)

    # Update the water molecules
    water_molecules.update(current_pressure_force, current_viscosity, current_gravity)  # Pass the gravity value to the update method

    # Update the GUI
    manager.update(pygame.time.get_ticks())

    # Draw everything
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(screen, PIPE_COLOR, pygame.Rect(SCREEN_WIDTH / 2 - PIPE_WIDTH / 2, 0, PIPE_WIDTH, PIPE_HEIGHT), 2)
    water_molecules.draw(screen)
    manager.draw_ui(screen)

    # Flip the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()