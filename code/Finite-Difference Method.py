import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import matplotlib.gridspec as gridspec
from matplotlib.backend_tools import Cursors

# Define the lake's size
Lx, Ly = 200, 200                    # Length and width of the lake
dx, dy = 1, 1                        # Spatial step size
nx, ny = int(Lx / dx), int(Ly / dy)  # Number of grid points

# Define time step size and diffusion coefficient
dt = 0.1  # Time step size
D = 2.0   # Diffusion coefficient

# Initialize the pollutant concentration matrix
C = np.zeros((nx, ny))

# Create a figure window
fig = plt.figure(figsize=(12, 8))
gs = gridspec.GridSpec(5, 2, width_ratios=[3, 1], height_ratios=[15, 1, 1, 1, 1])

# Initial plot
ax = fig.add_subplot(gs[:3, 0])
im = ax.imshow(C, extent=[0, Lx, 0, Ly], origin='lower', cmap='viridis', vmin=0, vmax=10)
plt.colorbar(im, ax=ax, label='Concentration')
annotation = ax.annotate('', xy=(0.95, 0.05), xycoords='axes fraction', ha='right',
                         bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="yellow"),
                         arrowprops=dict(arrowstyle="->"))
annotation.set_visible(False)
plt.draw()

# Track current cursor type
current_cursor = None
initial_radius = 5
initial_concentration = 10
radius = initial_radius  # Variable to store the pollution source radius
concentration = initial_concentration  # Variable to store the pollution source concentration

# Mouse click event handler
def onclick(event):
    if event.button == 1 and current_cursor == Cursors.POINTER:  # Left click to add initial pollution source
        iy, ix = int(event.xdata), int(event.ydata)
        for i in range(max(0, ix - radius), min(nx, ix + radius)):
            for j in range(max(0, iy - radius), min(ny, iy + radius)):
                if (i - ix)**2 + (j - iy)**2 <= radius**2:
                    C[i, j] = concentration
        update_plot()
    elif event.button == 3 and current_cursor == Cursors.POINTER:  # Right click to view pollutant concentration
        iy, ix = int(event.xdata / dx), int(event.ydata / dy)
        if 0 <= ix < nx and 0 <= iy < ny:
            conc = C[ix, iy]
            annotation.set_text(f'Pos: ({iy}, {ix})\nConc: {conc:.2f}')
            annotation.xy = (0.95, 0.05)
            annotation.set_visible(True)
            plt.draw()

# Close window event handler
def on_close(event):
    global running
    running = False

# Update plot function
def update_plot():
    im.set_data(C)
    ax.set_title('Pollutant Diffusion')
    plt.draw()

class Index:
    def rst(self, event):
        global C
        C.fill(0)  # Set all values in the concentration array to zero
        update_plot()

# Function to update the radius from the slider
def update_radius(val):
    global radius
    radius = int(slider_radius.val)

# Function to update the concentration from the slider
def update_concentration(val):
    global concentration
    concentration = slider_concentration.val

# Buttons in the right bottom corner
callback = Index()
axrst = fig.add_subplot(gs[3, 1])
axrst.set_position([0.72, 0.3, 0.1, 0.075])   # Manually set the position of the RESET button
brst = Button(axrst, 'RESET')
brst.on_clicked(callback.rst)

# Slider for pollution source radius in the top right
ax_slider_radius = fig.add_subplot(gs[0, 1])
slider_radius = Slider(ax_slider_radius, 'Radius', 1, 10, valinit=initial_radius, orientation='horizontal')
ax_slider_radius.set_position([0.72, 0.8, 0.2, 0.03])  # [left, bottom, width, height]
slider_radius.on_changed(update_radius)

# Slider for pollution source concentration in the middle right
ax_slider_concentration = fig.add_subplot(gs[1, 1])
slider_concentration = Slider(ax_slider_concentration, 'Concentration', 1, 10, valinit=initial_concentration, orientation='horizontal')
ax_slider_concentration.set_position([0.72, 0.7, 0.2, 0.03])  # [left, bottom, width, height]
slider_concentration.on_changed(update_concentration)

update_plot()

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

# Bind mouse click events and window close event
fig.canvas.mpl_connect('button_press_event', onclick)
fig.canvas.mpl_connect('close_event', on_close)
fig.canvas.mpl_connect('motion_notify_event', change_cursor)



# Simulation loop
running = True
while running:  
    # Vectorized calculation of the new concentration
    C_new = C.copy()
    C_new[1:nx-1, 1:ny-1] = C[1:nx-1, 1:ny-1] + D * dt * (
        (C[2:nx, 1:ny-1] - 2 * C[1:nx-1, 1:ny-1] + C[0:nx-2, 1:ny-1]) / dx**2 +
        (C[1:nx-1, 2:ny] - 2 * C[1:nx-1, 1:ny-1] + C[1:nx-1, 0:ny-2]) / dy**2
    )
    C = C_new
    
    # Real-time update of the image
    update_plot()
    plt.pause(0.001)  # Increase update frequency

plt.close(fig)
