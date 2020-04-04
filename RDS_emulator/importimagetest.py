from PIL import Image as PIL_image
import numpy

res = numpy.array(PIL_image.open("images/testimage.jpg"))

PIL_image.fromarray(res).show()
