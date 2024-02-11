import matplotlib.pyplot as plt
import numpy as np

# Generate random numbers
np.random.seed(0)
x = np.random.rand(100)
y = np.random.rand(100)

# Create a scatter plot
plt.scatter(x, y)

# Add labels and title
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Random Numbers Plot')

# Display the plot
plt.show()
