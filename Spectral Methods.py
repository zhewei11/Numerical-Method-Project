import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider
import matplotlib.gridspec as gridspec
from matplotlib.backend_tools import Cursors
from scipy.fft import fft2, ifft2

# Define parameters
L = 100.0  # Region length
N = 100  # Number of grid points
D = 10  # Diffusion coefficient
T = 10.0  # Simulation time
dt = 0.01  # Time step
timesteps = int(T / dt)

# Define space and initial conditions
x = np.linspace(0, L, N, endpoint=False)
y = np.linspace(0, L, N, endpoint=False)
X, Y = np.meshgrid(x, y)
u0 = np.exp(-((X - L/2)**2 + (Y - L/2)**2))  # Gaussian initial distribution

# Fourier modes
kx = np.fft.fftfreq(N, L/N) * 2 * np.pi
ky = np.fft.fftfreq(N, L/N) * 2 * np.pi
KX, KY = np.meshgrid(kx, ky)
K2 = KX**2 + KY**2

# Initialize solution
u = u0.copy()
u_hat = fft2(u)

# Create a figure window
fig = plt.figure(figsize=(12, 8))
gs = gridspec.GridSpec(5, 2, width_ratios=[3, 1], height_ratios=[15, 1, 1, 1, 1])

# Track current cursor type and last click type
current_cursor = None
last_click_right = False
initial_radius = 5
initial_concentration = 10
radius = initial_radius  # Variable to store the pollution source radius
concentration = initial_concentration  # Variable to store the pollution source concentration

# Prepare the plot
ax = fig.add_subplot(gs[:, 0])
vmin = 0
vmax = 10

# Use imshow to plot the initial image
im = ax.imshow(u, extent=[0, L, 0, L], origin='lower', cmap='viridis', vmin=vmin, vmax=vmax, aspect='auto')
cbar = fig.colorbar(im, ax=ax, label='Pollutant Concentration')

# Set the title and axis labels
ax.set_title('Pollutant Diffusion')
ax.set_xlabel('x')
ax.set_ylabel('y')

# Initialize right-click annotation
annotation = ax.annotate('', xy=(0, 0), xycoords='data', bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))

# Update function for animation
def update(frame):
    global u_hat, u, last_click_right
    u_hat = u_hat * np.exp(-D * K2 * dt)  # Time evolution
    u = np.real(ifft2(u_hat))  # Inverse transform to get real space solution
    im.set_data(u)
    if not last_click_right:
        annotation.set_visible(False)  # Hide annotation if the last click was not right-click
    return im,

# Mouse click event handler
def onclick(event):
    global last_click_right
    if event.xdata is not None and event.ydata is not None:
        ix, iy = int(event.xdata * N / L), int(event.ydata * N / L)
        if event.button == 1 and current_cursor == Cursors.POINTER:  # Left-click to add initial pollutant source
            last_click_right = False
            for i in range(max(0, ix - radius), min(N, ix + radius)):
                for j in range(max(0, iy - radius), min(N, iy + radius)):
                    if (i - ix)**2 + (j - iy)**2 <= radius**2:
                        u[j, i] += concentration  # Add pollutant source
            global u_hat
            u_hat = fft2(u)  # Update Fourier transform
        elif event.button == 3 and current_cursor == Cursors.POINTER:  # Right-click to view concentration
            last_click_right = True
            conc = u[iy, ix]
            annotation.xy = (event.xdata, event.ydata)
            annotation.set_text(f'({event.xdata:.1f}, {event.ydata:.1f})\nConcentration: {conc:.2f}')
            annotation.set_visible(True)
            plt.draw()

# Close window event handler
def on_close(event):
    global running
    running = False

# Update plot function
def update_plot():
    im.set_data(u)
    ax.set_title('Pollutant Diffusion')
    plt.draw()

class Index:
    def rst(self, event):
        global u, u_hat
        u.fill(0)  # Set all values in the concentration array to zero
        u_hat = fft2(u)  # Update Fourier transform
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

# Change cursor type based on position
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

# Create animation
ani = FuncAnimation(fig, update, frames=timesteps, blit=False, repeat=False)

# Show plot
plt.show()
