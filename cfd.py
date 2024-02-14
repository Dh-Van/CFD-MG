import pygame
import pygame_gui
import random
import numpy as np
import csv
from tqdm import tqdm

# Define some constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 900
PIPE_WIDTH, PIPE_HEIGHT = 100, SCREEN_HEIGHT
PIPE_COLOR = (255, 255, 255)  # White
BACKGROUND_COLOR = (0, 0, 0)  # Black
WATER_COLOR = (255, 0, 0)  # Light blue
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
        self.velocities = []
        self.max_velocities = 100  # Maximum number of velocities to consider for the rolling average

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

    def add_molecule(self, num_molecules=10):
        for _ in range(num_molecules):
            x = random.uniform(SCREEN_WIDTH / 2 - PIPE_WIDTH / 2, SCREEN_WIDTH / 2 + PIPE_WIDTH / 2)
            y = 0
            water_molecule = WaterMolecule(x, y)
            self.water_molecules.add(water_molecule)

    def update_molecules(self):
        self.water_molecules.update(self.pressure_force, self.viscosity, self.gravity)
        for molecule in self.water_molecules:
            self.velocities.append(np.linalg.norm(molecule.speed))  # Add the magnitude of the velocity vector
            if len(self.velocities) > self.max_velocities:
                self.velocities.pop(0)  # Remove the oldest velocity if we've reached the maximum

    def draw_molecules(self, screen):
        self.water_molecules.draw(screen)

    def get_average_velocity(self):
        if self.velocities:
            return sum(self.velocities) / len(self.velocities)
        else:
            return 0

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

class DataCollector:
    def __init__(self, file_name, pressure_bounds, viscosity_bounds, gravity_bounds):
        self.file_name = file_name
        self.pressure_bounds = np.arange(pressure_bounds[0], pressure_bounds[1], 0.05)
        self.viscosity_bounds = np.arange(viscosity_bounds[0], viscosity_bounds[1], 0.05)
        self.gravity_bounds = np.arange(gravity_bounds[0], gravity_bounds[1], 0.05)

    def run_pressure_simulations(self, viscosity, gravity):
        for pressure in tqdm(self.pressure_bounds, desc="Pressure simulations"):
            simulation = Simulation(pressure, viscosity, gravity)
            average_velocity = self.run_simulation(simulation, pressure, viscosity, gravity)
            with open(self.file_name + ".csv", 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([pressure, average_velocity])

    def run_viscosity_simulations(self, pressure, gravity):
        for viscosity in tqdm(self.viscosity_bounds, desc="Viscosity simulations"):
            simulation = Simulation(pressure, viscosity, gravity)
            average_velocity = self.run_simulation(simulation, pressure, viscosity, gravity)
            with open(self.file_name + ".csv", 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([viscosity, average_velocity])

    def run_gravity_simulations(self, pressure, viscosity):
        for gravity in tqdm(self.gravity_bounds, desc="Gravity simulations"):
            simulation = Simulation(pressure, viscosity, gravity)
            average_velocity = self.run_simulation(simulation, pressure, viscosity, gravity)
            with open(self.file_name + ".csv", 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([gravity, average_velocity])

    def run_simulation(self, simulation, pressure, viscosity, gravity):
        for _ in tqdm(range(400), desc="Simulation steps"):  # Run the simulation for 1000 steps
            simulation.add_molecule()
            simulation.update_molecules()
        return simulation.get_average_velocity()

    def write_to_csv(self, pressure, viscosity, gravity, average_velocity):
        with open(self.file_name + ".csv", 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([pressure, viscosity, gravity, average_velocity])

class Main:
    def __init__(self):
        pass

    def run_simulation_gui(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.simulation = Simulation(0.1, 0.99, 0.1)
        self.gui = GUI(self.manager, self.simulation)
        running = True
        while running:
            time_delta = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                self.manager.process_events(event)
                self.gui.process_events(event)

            self.manager.update(time_delta)

            self.screen.fill(BACKGROUND_COLOR)
            pygame.draw.line(self.screen, PIPE_COLOR, (SCREEN_WIDTH / 2 - PIPE_WIDTH / 2, 0), (SCREEN_WIDTH / 2 - PIPE_WIDTH / 2, SCREEN_HEIGHT), 2)
            pygame.draw.line(self.screen, PIPE_COLOR, (SCREEN_WIDTH / 2 + PIPE_WIDTH / 2, 0), (SCREEN_WIDTH / 2 + PIPE_WIDTH / 2, SCREEN_HEIGHT), 2)

            self.simulation.add_molecule()
            self.simulation.update_molecules()
            self.simulation.draw_molecules(self.screen)

            self.manager.draw_ui(self.screen)

            print(self.simulation.get_average_velocity())

            pygame.display.flip()

        pygame.quit()

    def collect_data(self, pressure_bounds, viscosity_bounds, gravity_bounds):
        gravity = DataCollector("gravity", pressure_bounds, viscosity_bounds, gravity_bounds)
        gravity.run_gravity_simulations(0.1, 0.5)
        viscocity = DataCollector("viscocity", pressure_bounds, viscosity_bounds, gravity_bounds)
        viscocity.run_viscosity_simulations(0.1, 0.5)
        pressure = DataCollector("pressure", pressure_bounds, viscosity_bounds, gravity_bounds)
        pressure.run_pressure_simulations(0.1, 0.5)

if __name__ == '__main__':
   cfd = Main()
   cfd.run_simulation_gui()
#    cfd.collect_data((0, 1.0), (0, 1.0), (0, 1.0))