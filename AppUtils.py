import os
import sys


def get_resource_path(relative_path=''):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_config_path(app_name='my_App'):
    if hasattr(sys, "_MEIPASS"):
        abs_home = os.path.abspath(os.path.expanduser("~"))
        abs_dir_app = os.path.join(abs_home, f"."+app_name)
        if not os.path.exists(abs_dir_app):
            os.mkdir(abs_dir_app)
        cfg_path = os.path.join(abs_dir_app, "data")
    else:
        cfg_path = os.path.abspath(".%sdata" % os.sep)
    return cfg_path


def get_exe_path() -> str:
    # determine if application is a script file or frozen exe
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    return application_path


def create_path_it_not_exist(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path
