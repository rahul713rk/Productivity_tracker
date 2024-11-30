import os
from pathlib import Path

# Step 1: Define the desktop entry content
def create_desktop_entry(base_dir):
    # Get the absolute paths for app.py and icon.svg
    app_path = os.path.join(base_dir, "app.py")
    icon_path = os.path.join(base_dir, "resources/others/icon.svg")

    desktop_entry = f"""[Desktop Entry]
Version=4.0
Type=Application
Name=Productivity Tracker
Exec=python3 {app_path}
Icon={icon_path}
Terminal=true
Categories=Utility;Application;
"""
    return desktop_entry

# Step 2: Write the desktop entry to a .desktop file
def generate_desktop_file(base_dir):
    desktop_filename = "ProductivityTracker.desktop"
    with open(desktop_filename, "w") as file:
        file.write(create_desktop_entry(base_dir))
    return desktop_filename

# Step 3: Make the file executable
def make_executable(file_path):
    os.chmod(file_path, 0o755)

# Step 4: Move the file to the application menu
def move_to_applications(file_path):
    applications_dir = os.path.join(str(Path.home()), ".local/share/applications")
    if not os.path.exists(applications_dir):
        os.makedirs(applications_dir)
    os.rename(file_path, os.path.join(applications_dir, file_path))

# Main function to run all steps
def main():
    # Get the current directory where this script is being run from
    base_dir = os.path.abspath(os.path.dirname(__file__))

    # Generate the .desktop file
    desktop_file = generate_desktop_file(base_dir)

    # Make the .desktop file executable
    make_executable(desktop_file)

    # Move the .desktop file to the application menu
    move_to_applications(desktop_file)

    print("Shortcut created and moved to Application Menu successfully.")

if __name__ == "__main__":
    main()
