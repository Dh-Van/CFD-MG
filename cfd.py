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

class Simulation:
    def __init__(self, pressure_force, viscosity, gravity):
        self.pressure_force = pressure_force
        self.viscosity = viscosity
        self.gravity = gravity
        self.water_molecules = pygame.sprite.Group()

    def get_pressure_force(self):
        return self.pressure_force

    def set_pressure_force(self, pressure_force):
        self.pressure_force = pressure_force

    def get_viscosity(self):
        return self.viscosity

    def set_viscosity(self, viscosity):
        self.viscosity = viscosity

    def get_gravity(self):
        return self.gravity

    def set_gravity(self, gravity):
        self.gravity = gravity

    def add_molecule(self):
        x = random.uniform(SCREEN_WIDTH / 2 - PIPE_WIDTH / 2, SCREEN_WIDTH / 2 + PIPE_WIDTH / 2)
        y = 0
        water_molecule = WaterMolecule(x, y)
        self.water_molecules.add(water_molecule)

    def update_molecules(self):
        self.water_molecules.update(self.pressure_force, self.viscosity, self.gravity)

    def draw_molecules(self, screen):
        self.water_molecules.draw(screen)

class GUI:
    def __init__(self, manager, simulation):
        self.manager = manager
        self.simulation = simulation

        # Create sliders for pressure force, viscosity and gravity
        self.pressure_force_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, 70), (200, 20)),
                                                               start_value=simulation.get_pressure_force(),
                                                               value_range=(0.0, 1.0),
                                                               manager=manager)
        self.viscosity_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, 120), (200, 20)),
                                                          start_value=simulation.get_viscosity(),
                                                          value_range=(0.9, 1.0),
                                                          manager=manager)
        self.gravity_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, 170), (200, 20)),
                                                        start_value=simulation.get_gravity(),
                                                        value_range=(0.0, 0.5),
                                                        manager=manager)

        # Create labels for the sliders
        self.pressure_force_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, 50), (200, 20)),
                                                   text='Pressure Force',
                                                   manager=manager)
        self.viscosity_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, 100), (200, 20)),
                                              text='Viscosity',
                                              manager=manager)
        self.gravity_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, 150), (200, 20)),
                                            text='Gravity',
                                            manager=manager)

    def process_events(self, event):
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == self.pressure_force_slider:
                    self.simulation.set_pressure_force(self.pressure_force_slider.get_current_value())
                elif event.ui_element == self.viscosity_slider:
                    self.simulation.set_viscosity(self.viscosity_slider.get_current_value())
                elif event.ui_element == self.gravity_slider:
                    self.simulation.set_gravity(self.gravity_slider.get_current_value())

def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

    simulation = Simulation(0.1, 0.99, 0.1)
    gui = GUI(manager, simulation)

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            manager.process_events(event)
            gui.process_events(event)

        manager.update(time_delta)

        screen.fill(BACKGROUND_COLOR)
        pygame.draw.line(screen, PIPE_COLOR, (SCREEN_WIDTH / 2 - PIPE_WIDTH / 2, 0), (SCREEN_WIDTH / 2 - PIPE_WIDTH / 2, SCREEN_HEIGHT), 2)
        pygame.draw.line(screen, PIPE_COLOR, (SCREEN_WIDTH / 2 + PIPE_WIDTH / 2, 0), (SCREEN_WIDTH / 2 + PIPE_WIDTH / 2, SCREEN_HEIGHT), 2)

        for _ in range(10):  # Add 10 molecules per frame
            simulation.add_molecule()
        simulation.update_molecules()
        simulation.draw_molecules(screen)

        manager.draw_ui(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()