import unittest
import sys
sys.path.append('..')
from track_preprocessing import preprocess_curvature

class TestCurvaturePreprocessing(unittest.TestCase):

    def setUp(self):

        self.curvatures = {"units": {"position": "m", "radius at start": "m", "radius at end": "m"}, 
                           "values": [[0.0, -502, -502], [1018.8, 0.0, -850.0]]}
        
        self.file_content = {"field1": {}, "curvatures": self.curvatures, "field2": {}}


    def test_track_without_curvature_field(self):

        del self.file_content["curvatures"]

        file_content_without_curvatures = self.file_content

        with self.assertRaises(ValueError) as exc:

            preprocess_curvature(file_content_without_curvatures)

        self.assertEqual(str(exc.exception), "File does not contain curvature field! Aborting.")


    def test_track_without_unit_field(self):

        del self.file_content["curvatures"]["units"]

        file_content_without_units = self.file_content

        with self.assertRaises(ValueError) as exc:

            preprocess_curvature(file_content_without_units)

        self.assertEqual(str(exc.exception), "\"units\" or \"values\" field is missing! Aborting.")


    def test_curvature_without_radius_at_start(self):

        del self.file_content["curvatures"]["units"]["radius at start"]

        file_content_without_units = self.file_content

        with self.assertRaises(ValueError) as exc:

            preprocess_curvature(file_content_without_units)

        self.assertEqual(str(exc.exception), "Dictionary must contain \"position\", \"radius at start\", and \"radius at end\" but one (or more) is missing! Aborting.")


    def test_verify_result(self):

        expected_result = dict(self.file_content)

        expected_result["curvatures"] = {"units": {"position": "m", "radius": "m"}, 
                                        "values": [[0.0, 502], [1018.8, 425]]}

        result = preprocess_curvature(self.file_content)

        self.assertEqual(result, expected_result)


if __name__ == '__main__':

    unittest.main()