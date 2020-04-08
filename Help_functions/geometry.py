"""
Note: Import this file to needed directory.
"""

class ElementsError(Exception):
    pass

def check_point(tuple_point):
    if  type(tuple_point) != tuple or type(tuple_point[0]) != int or type(tuple_point[1]) != int:
        error_message = "point invalid format"
        raise ElementsError(error_message)

    if len(tuple_point) != 2:
        error_message = "point invalid format"
        raise ElementsError(error_message)

class polygon:
    def __init__(self, points):
        self.number_of_points = 0
        self.points = points

        for point in points:
            self.number_of_points += 1;

        # Atleast three points are needed to form a polygon.
        if self.number_of_points < 3:
            error_message = f"Expected 3 or more elements but only recieved {self.number_of_points}"
            raise ElementsError(error_message)

    # Function taken from https://en.wikipedia.org/wiki/Even%E2%80%93odd_rule.
    def inside_polygon(self, point):
        """Determine if the point is in the path.

        Args:
          point -- tuple of: (x-cordinate, y-cordinate)

        Returns:
          True if the point is in the path.
        """
        check_point(point) # Check the point's format

        x = point[0]
        y = point[1]
        poly = self.points
        num = len(poly)
        i = 0
        j = num - 1
        c = False
        for i in range(num):
            if ((poly[i][1] > y) != (poly[j][1] > y)) and \
                    (x < poly[i][0] + (poly[j][0] - poly[i][0]) * (y - poly[i][1]) /
                                      (poly[j][1] - poly[i][1])):
                c = not c
            j = i
        return c

# Function taken from https://en.wikipedia.org/wiki/Even%E2%80%93odd_rule.
# Use this if you don't want to create a polygon object.
def inside_polygon(point, poly) -> bool:
    """Determine if the point is in the path.

    Args:
      point -- tuple of: (x-cordinate, y-cordinate)
      poly -- a list of tuples [(x, y), (x, y), ...]

    Returns:
      True if the point is in the path.
    """
    if len(poly) < 3:
        error_message = f"Expected 3 or more elements but only recieved {len(poly)}"
        raise ElementsError(error_message)
    check_point(point) # Check the point's format

    x = point[0]
    y = point[1]
    num = len(poly)
    i = 0
    j = num - 1
    c = False
    for i in range(num):
        if ((poly[i][1] > y) != (poly[j][1] > y)) and \
                (x < poly[i][0] + (poly[j][0] - poly[i][0]) * (y - poly[i][1]) /
                                  (poly[j][1] - poly[i][1])):
            c = not c
        j = i
    return c


