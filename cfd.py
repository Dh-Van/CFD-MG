import numpy as np
import matplotlib.pyplot as plt

class CFDModel:
    def __init__(self, nx, ny, dx, dy, dt):
        self.nx = nx  # Number of grid points in x-direction
        self.ny = ny  # Number of grid points in y-direction
        self.dx = dx  # Grid spacing in x-direction
        self.dy = dy  # Grid spacing in y-direction
        self.dt = dt  # Time step size
        self.rho = 1.0  # Fluid density

        # Initialize velocity and pressure fields
        self.u = np.zeros((nx, ny))  # x-velocity
        self.v = np.zeros((nx, ny))  # y-velocity
        self.p = np.zeros((nx, ny))  # pressure

    def solve(self, num_steps):
        for _ in range(num_steps):
            # Perform one time step of the CFD simulation
            self.calculate_velocity()
            self.calculate_pressure()
            self.update_velocity()

            # Visualize the velocity field
            self.plot_velocity()

    def calculate_velocity(self):
        # Implement the velocity calculation using the Navier-Stokes equations
        for i in range(1, self.nx - 1):
            for j in range(1, self.ny - 1):
                self.u[i, j] = self.u[i, j] + self.dt * (
                    -self.u[i, j] * (self.u[i, j] - self.u[i - 1, j]) / self.dx
                    - self.v[i, j] * (self.u[i, j] - self.u[i, j - 1]) / self.dy
                )
                self.v[i, j] = self.v[i, j] + self.dt * (
                    -self.u[i, j] * (self.v[i, j] - self.v[i - 1, j]) / self.dx
                    - self.v[i, j] * (self.v[i, j] - self.v[i, j - 1]) / self.dy
                )

    def calculate_pressure(self):
        # Implement the pressure calculation using the Poisson equation
        self.p[1:-1, 1:-1] = (
            ((self.p[2:, 1:-1] + self.p[:-2, 1:-1]) * self.dy**2
            + (self.p[1:-1, 2:] + self.p[1:-1, :-2]) * self.dx**2)
            / (2 * (self.dx**2 + self.dy**2))
            - self.rho * self.dx**2 * self.dy**2 / (2 * (self.dx**2 + self.dy**2))
            * (self.u[2:, 1:-1] - self.u[:-2, 1:-1]) / self.dx
            * (self.v[1:-1, 2:] - self.v[1:-1, :-2]) / self.dy
        )

    def update_velocity(self):
        # Implement the velocity update using the pressure correction
        self.u[1:-1, 1:-1] = self.u[1:-1, 1:-1] - self.dt * (
            (self.p[2:, 1:-1] - self.p[:-2, 1:-1]) / (2 * self.dx)
            - self.rho * (self.p[1:-1, 2:] - self.p[1:-1, :-2]) / (2 * self.dy)
        )
        self.v[1:-1, 1:-1] = self.v[1:-1, 1:-1] - self.dt * (
            (self.p[1:-1, 2:] - self.p[1:-1, :-2]) / (2 * self.dy)
            - self.rho * (self.p[2:, 1:-1] - self.p[:-2, 1:-1]) / (2 * self.dx)
        )

    def plot_velocity(self):
        # Plot the velocity field
        x = np.arange(0, self.nx) * self.dx
        y = np.arange(0, self.ny) * self.dy
        X, Y = np.meshgrid(x, y)

        plt.figure()
        plt.quiver(X, Y, self.u, self.v)
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Velocity Field')
        plt.show()
        plt.close()  # Close the figure to prevent accumulation of open figures

if __name__ == "__main__":
    nx = 10  # Number of grid points in x-direction
    ny = 10  # Number of grid points in y-direction
    dx = 1.0  # Grid spacing in x-direction
    dy = 1.0  # Grid spacing in y-direction
    dt = 0.1  # Time step size
    num_steps = 100  # Number of simulation steps

    model = CFDModel(nx, ny, dx, dy, dt)
    model.solve(num_steps)
