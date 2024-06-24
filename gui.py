import flet as ft
import matplotlib.pyplot as plt
import numpy as np
import io
from PIL import Image
import subprocess
import sys

# Function to run the selected mode script and generate the plot
def run_mode_script(mode):
    if mode == "Finite-Difference Method":
        script_path = "Finite-Difference Method.py"
    elif mode == "Forword Euler Method":
        script_path = "Forword Euler Method.py"
    elif mode == "Spectral Methods":
        script_path = "Spectral Methods.py"

    else:
        plt.figure()
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        plt.plot(x, y)
        plt.title("Default Mode")
        plt.savefig("default_mode_plot.png")
        return "default_mode_plot.png"

    # Run the script using subprocess
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    # Assuming the scripts save the plots with a specific name
    plot_path = f"{mode.lower().replace(' ', '_')}_plot.png"
    return plot_path

# Function to display the plot in the Flet application
def display_plot(page, plot_path):
    # Read the plot image
    img = Image.open(plot_path)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_data = buffer.getvalue()

    # Create an Flet Image control with the plot
    plot_image = ft.Image(
        src_base64=img_data,
        width=600,
        height=400,
        fit=ft.ImageFit.CONTAIN,
    )

    # Add the image to the page
    page.controls.clear()
    page.add(plot_image)
    page.update()

def main(page: ft.Page):
    page.title = "Pollution Simulation"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Set initial window size and make it non-resizable
    page.window_width = 800
    page.window_height = 600
    page.window_resizable = False

    # Title
    title = ft.Text("Pool Water Pollution Simulation", size=30, weight="bold", style=ft.TextThemeStyle.HEADLINE_SMALL)

    # Image (assuming 'lake.jpg' is in the current directory)
    img = ft.Image(
        src="lake2.jpg",
        width=400,
        height=400,
        fit=ft.ImageFit.CONTAIN,
    )

    # Mode selection dropdown with shorter width
    mode_dropdown = ft.Dropdown(
        label="Select Mode",
        width=300,
        options=[
            ft.dropdown.Option("Finite-Difference Method"),
            ft.dropdown.Option("Forword Euler Method"),
            ft.dropdown.Option("Spectral Methods")
        ]
    )

    # Start button click event handler
    def start_button_click(e):
        selected_mode = mode_dropdown.value
        plot_path = run_mode_script(selected_mode)
        display_plot(page, plot_path)

    # Start button
    start_button = ft.ElevatedButton(
        text="Start",
        on_click=start_button_click
    )

    # Left column for title and image
    left_column = ft.Column(
        controls=[
            title,
            img,
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # Right column for dropdown and start button
    right_column = ft.Column(
        controls=[
            mode_dropdown,
            start_button,
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # Add left and right columns to a row
    page.add(
        ft.Row(
            controls=[
                left_column,
                right_column,
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
    )

    # Handle the window close event
    def window_event_handler(e):
        if e.data == "close":
            sys.exit()

    page.window_event_handler = window_event_handler

if __name__ == "__main__":
    ft.app(target=main)
