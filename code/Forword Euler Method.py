import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import matplotlib.gridspec as gridspec
from matplotlib.backend_tools import Cursors

# Parameters
Lx, Ly = 100, 100    # Length of the lake (square domain)
dx, dy = 0.5, 0.5    # Grid spacing
nx, ny = int(Lx / dx), int(Ly / dy)
D = 10.0             # Diffusion coefficient
dt = 0.01            # Time step size

# Initialize concentration array
u = np.zeros((nx, ny))
# Initial concentration spike in the middle in a circular shape
cx, cy = nx // 2, ny // 2
initial_radius = 5  # Initial radius of the pollution source
initial_concentration = 10.0  # Initial concentration of the pollution source
for i in range(nx):
    for j in range(ny):
        if (i - cx)**2 + (j - cy)**2 <= initial_radius**2:
            u[i, j] = 1.0

# Track current cursor type
current_cursor = None
radius = initial_radius  # Variable to store the pollution source radius
concentration = initial_concentration  # Variable to store the pollution source concentration

# Function to add pollution source
def add_pollution(event):
    if event.button == 1 and current_cursor == Cursors.POINTER:  # Left click and cursor is POINTER
        iy, ix = int(event.xdata / dx), int(event.ydata / dy)
        for i in range(max(0, ix - radius), min(nx, ix + radius)):
            for j in range(max(0, iy - radius), min(ny, iy + radius)):
                if (i - ix)**2 + (j - iy)**2 <= radius**2:
                    u[i, j] = concentration
        update_plot()

def show_concentration(event):
    if event.button == 3 and current_cursor == Cursors.POINTER:  # Right click
        iy, ix = int(event.xdata / dx), int(event.ydata / dy)
        if 0 <= iy < nx and 0 <= ix < ny:
            concentration = u[ix, iy]
            annotation.set_text(f'Pos: ({iy}, {ix})\nConc: {concentration:.2f}')
            annotation.xy = (0.95, 0.05)
            annotation.set_visible(True)
            plt.draw()

def on_close(event):
    global running
    running = False

# Update plot function
def update_plot():
    im.set_data(u)
    ax.set_title('Pollutant Diffusion')
    plt.draw()

class Index:
    ind = 0

    def rst(self, event):
        global u
        u.fill(0)  # Set all values in the concentration array to zero
        update_plot()

# Function to update the radius from the slider
def update_radius(val):
    global radius
    radius = int(slider_radius.val)

# Function to update the concentration from the slider
def update_concentration(val):
    global concentration
    concentration = slider_concentration.val

# Setup plot with GridSpec
fig = plt.figure(figsize=(12, 8))
gs = gridspec.GridSpec(4, 2, width_ratios=[3, 1], height_ratios=[15, 1, 1, 1])

# Plot in the left column, spanning all rows
ax = fig.add_subplot(gs[:, 0])
im = ax.imshow(u, extent=[0, Lx, 0, Ly], origin='lower', cmap='viridis', vmin=0, vmax=10)
plt.colorbar(im, ax=ax, label='Concentration')
annotation = ax.annotate('', xy=(0.95, 0.05), xycoords='axes fraction', ha='right',
                         bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="yellow"),
                         arrowprops=dict(arrowstyle="->"))
annotation.set_visible(False)
plt.draw()

# Buttons in the right bottom corner
callback = Index()
axrst = fig.add_subplot(gs[2, 1])
axrst.set_position([0.72, 0.4, 0.1, 0.075])   # Manually set the position of the RESET button
brst = Button(axrst, 'RESET')
brst.on_clicked(callback.rst)

# Slider for pollution source radius in the top right
ax_slider_radius = fig.add_subplot(gs[0, 1])
slider_radius = Slider(ax_slider_radius, 'Radius', 1, 10, valinit=initial_radius, orientation='horizontal')
ax_slider_radius.set_position([0.72, 0.75, 0.2, 0.05])  # [left, bottom, width, height]
slider_radius.on_changed(update_radius)

# Slider for pollution source concentration in the middle right
ax_slider_concentration = fig.add_subplot(gs[1, 1])
slider_concentration = Slider(ax_slider_concentration, 'Concentration', 1, 10, valinit=initial_concentration, orientation='horizontal')
ax_slider_concentration.set_position([0.72, 0.65, 0.2, 0.05])  # [left, bottom, width, height]
slider_concentration.on_changed(update_concentration)

update_plot()

# Function to change cursor style
def change_cursor(event):
    global current_cursor
    if event.inaxes in [axrst, ax_slider_radius, ax_slider_concentration]:
        fig.canvas.set_cursor(Cursors.HAND)
        current_cursor = Cursors.HAND
    elif event.inaxes == ax:
        fig.canvas.set_cursor(Cursors.POINTER)
        current_cursor = Cursors.POINTER
    else:
        fig.canvas.set_cursor(Cursors.POINTER)
        current_cursor = Cursors.POINTER

# Connect the click and close events
fig.canvas.mpl_connect('button_press_event', add_pollution)
fig.canvas.mpl_connect('button_press_event', show_concentration)
fig.canvas.mpl_connect('close_event', on_close)
fig.canvas.mpl_connect('motion_notify_event', change_cursor)

# Simulation loop
running = True
while running:  # Infinite loop until window is closed
    # Compute fluxes (diffusion)
    flux_x = D * (np.roll(u, -1, axis=0) - np.roll(u, 1, axis=0)) / (2 * dx)
    flux_y = D * (np.roll(u, -1, axis=1) - np.roll(u, 1, axis=1)) / (2 * dy)

    # Update concentration using Forward Euler method
    u += dt * (flux_x - np.roll(flux_x, 1, axis=0) + flux_y - np.roll(flux_y, 1, axis=1))

    # Boundary conditions (no-flux)
    u[0, :] = u[1, :]
    u[-1, :] = u[-2, :]
    u[:, 0] = u[:, 1]
    u[:, -1] = u[:, -2]

    # Update plot
    update_plot()
    plt.pause(0.01)  # Adjust the pause time as needed

plt.close(fig)
