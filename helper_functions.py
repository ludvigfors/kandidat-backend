import os, platform


def get_path_from_root(path):

    path_list = path.split("/")
    res = os.path.dirname(__file__)

    if platform.system() == "Windows":
        res += "\\".join(path_list)
    else:
        res += path

    return res


def check_request(request):
    pass