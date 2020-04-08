from Help_functions import geometry as help_geo
import unittest
import coverage

polygon1 = [(50,50), (50,100), (100,100), (100,50)]
polygon2 = [(0,0), (50,50), (50,0)]
polygon3 = [(10,30), (20,40), (40,20), (10,-10)]

class TestGeometry(unittest.TestCase):
    def test_valid_polygon(self):
        polygon_object = help_geo.polygon(polygon1)

        self.assertEqual(polygon_object.points, polygon1)
        self.assertEqual(len(polygon1), polygon_object.number_of_points)

    def test_invalid_polygon(self):
        invalid_polygon = [(10,10), (0,0)]
        self.assertRaises(help_geo.ElementsError, help_geo.polygon, invalid_polygon)
        self.assertRaises(help_geo.ElementsError, help_geo.inside_polygon, invalid_polygon, (0,0))

    def test_invalid_point(self):
        invalid_point1 = 0
        self.assertRaises(help_geo.ElementsError, help_geo.inside_polygon, invalid_point1, polygon1)

        invalid_point2 = (0,0,0)
        self.assertRaises(help_geo.ElementsError, help_geo.inside_polygon, invalid_point2, polygon1)

        invalid_point3 = (1, "a")
        self.assertRaises(help_geo.ElementsError, help_geo.inside_polygon, invalid_point3, polygon1)

    """Create a polygon object"""
    def test_polygon_inside_polygon1(self):
        polygon_object = help_geo.polygon(polygon1)

        point_within = (75,75) # Center point
        self.assertTrue(polygon_object.inside_polygon(point_within))

        point_outside = (10,10)
        self.assertFalse(polygon_object.inside_polygon(point_outside))

    def test_polygon_inside_polygon2(self):
        polygon_object = help_geo.polygon(polygon2)

        point_within1 = (30,30)
        self.assertTrue(polygon_object.inside_polygon(point_within1))
        point_within2 = (49,20)
        self.assertTrue(polygon_object.inside_polygon(point_within2))

        point_outside1 = (11,12)
        self.assertFalse(polygon_object.inside_polygon(point_outside1))
        point_outside2 = (51,50)
        self.assertFalse(polygon_object.inside_polygon(point_outside2))

    def test_polygon_inside_polygon3(self):
        polygon_object = help_geo.polygon(polygon3)

        point_within1 = (30,20)
        self.assertTrue(polygon_object.inside_polygon(point_within1))
        point_within2 = (11,-5)
        self.assertTrue(polygon_object.inside_polygon(point_within2))

        point_outside1 = (20,-1)
        self.assertFalse(polygon_object.inside_polygon(point_outside1))
        point_outside2 = (25,36)
        self.assertFalse(polygon_object.inside_polygon(point_outside2))



    """Does not create a polygon object """
    def test_inside_polygon1(self):
        point_within = (75,75) # Center point
        self.assertTrue(help_geo.inside_polygon(point_within, polygon1))

        point_outside = (10,10)
        self.assertFalse(help_geo.inside_polygon(point_outside, polygon1))

    def test_inside_polygon2(self):
        point_within1 = (30,30)
        self.assertTrue(help_geo.inside_polygon(point_within1, polygon2))
        point_within2 = (49,20)
        self.assertTrue(help_geo.inside_polygon(point_within2, polygon2))

        point_outside1 = (11,12)
        self.assertFalse(help_geo.inside_polygon(point_outside1, polygon2))
        point_outside2 = (51,50)
        self.assertFalse(help_geo.inside_polygon(point_outside2, polygon2))

    def test_inside_polygon3(self):
        point_within1 = (30,20)
        self.assertTrue(help_geo.inside_polygon(point_within1, polygon3))
        point_within2 = (11,-5)
        self.assertTrue(help_geo.inside_polygon(point_within2, polygon3))

        point_outside1 = (20,-1)
        self.assertFalse(help_geo.inside_polygon(point_outside1, polygon3))
        point_outside2 = (25,36)
        self.assertFalse(help_geo.inside_polygon(point_outside2, polygon3))

if __name__ == "__main__":
    unittest.main()
