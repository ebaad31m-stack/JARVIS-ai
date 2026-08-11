import os
import sys
import shutil


APP_NAME = "JARVIS"


def get_app_dir():
    """
    Returns the directory containing the JARVIS application.

    During development:
        C:\\JARVIS

    When packaged with PyInstaller:
        Uses the bundled application directory.
    """

    if getattr(sys, "frozen", False):
        return os.path.dirname(
            sys.executable
        )

    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )


def get_bundle_dir():
    """
    Returns the temporary PyInstaller bundle directory
    when running as a packaged application.
    """

    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS

    return get_app_dir()


def get_user_root():
    """
    Returns:

    C:\\Users\\USERNAME\\AppData\\Local\\JARVIS
    """

    local_app_data = os.environ.get(
        "LOCALAPPDATA"
    )

    if not local_app_data:
        local_app_data = os.path.expanduser(
            "~\\AppData\\Local"
        )

    path = os.path.join(
        local_app_data,
        APP_NAME
    )

    os.makedirs(
        path,
        exist_ok=True
    )

    return path


def get_user_data_dir():
    path = os.path.join(
        get_user_root(),
        "data"
    )

    os.makedirs(
        path,
        exist_ok=True
    )

    return path


def user_file(filename):
    return os.path.join(
        get_user_data_dir(),
        filename
    )


def resource_file(*parts):
    """
    Returns a file bundled with JARVIS.
    """

    return os.path.join(
        get_bundle_dir(),
        *parts
    )


def old_project_data_file(filename):
    """
    Used only for migrating old development files
    from C:\\JARVIS\\data.
    """

    return os.path.join(
        get_app_dir(),
        "data",
        filename
    )


def migrate_file(filename):
    """
    If an older JARVIS data file exists inside the
    project folder, copy it to the new user folder.

    Existing destination files are never overwritten.
    """

    old_path = old_project_data_file(
        filename
    )

    new_path = user_file(
        filename
    )

    if (
        os.path.exists(old_path)
        and not os.path.exists(new_path)
    ):
        try:
            shutil.copy2(
                old_path,
                new_path
            )

            print(
                f"Migrated {filename} to:"
            )

            print(
                new_path
            )

        except Exception as error:
            print(
                f"Could not migrate {filename}:",
                error
            )

    return new_path


def initialize_user_data():
    """
    Creates JARVIS user folders and migrates
    existing settings from the development version.
    """

    get_user_data_dir()

    files_to_migrate = [
        "ai_settings.json",
        "apps.json",
        "apps_detected.json",
        "contacts.json",
        "theme.json",
        "gmail_token.json",
        "config.json"
    ]

    for filename in files_to_migrate:
        migrate_file(
            filename
        )