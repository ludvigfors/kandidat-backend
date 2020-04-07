"""This is a playground for testing code"""
import numpy, datetime
from helper_functions import get_path_from_root
from PIL import Image as PIL_image

A = numpy.array(PIL_image.open(get_path_from_root("/RDS_emulator/images/testimage.jpg")))


folder_path = get_path_from_root("/IMM/images/")
jpg_image = PIL_image.fromarray(A)
now = datetime.datetime.now()
image_datetime = now.strftime("%Y-%m-%d_%H-%M-%S")
image_name = image_datetime + ".jpg"
image_path = folder_path + image_name
jpg_image.save(image_path)