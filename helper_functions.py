import os, platform


def get_path_from_root(path):
    """Returns the full path to the specified (relative) path. """
    path_list = path.split("/")
    res = os.path.dirname(__file__)  # Get the path to the directory where this file is located.

    if platform.system() == "Windows":
        res += "\\".join(path_list)
    else:
        res += path

    return res


def check_request(request):
    pass