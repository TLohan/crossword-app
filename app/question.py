""" question.py """

import re
from enum import Enum

class Orientation(Enum):
    ACROSS = 1
    DOWN = 2

class Question():
    """ Models a question.
    
    Args:
        position: The key for the question eg 1A or 3D
        text: the question
        answer: the answer to the question

    """

    def __init__(self, key, text, answer):
        self.key = key
        self.text = text
        self.answer = answer
        self.guess = ''
        self.guessed = False
        self.coordinates = (None, None)
    
    def length(self):
        """ Returns the length of the answer. """
        return len(self.answer)
    
    @property
    def key(self):
        return self.__key

    @key.setter
    def key(self, key):
        pattern = re.compile(r"^[1-9]\d?[AD]$")
        matches = re.match(pattern, key)

        if not matches:
            raise ValueError('Invalid key!')

        square_match = re.match(r"^[1-9]\d?", key)
        square = int(square_match.group(0))
        
        direction = key[-1]
        self.orientation = Orientation.ACROSS if direction == 'A' else Orientation.DOWN
        self.__key = "{}{}".format(square, direction)
    
    @property
    def coordinates(self):
        return self.__coordinates

    @coordinates.setter
    def coordinates(self, coords):
        self.coord_x = coords[0]
        self.coord_y = coords[1]
        self.__coordinates = coords

if __name__ == '__main__':
    import unittest

    class BoardTest(unittest.TestCase):

        def setUp(self):
            print('In SetUp')
            self.valid_question = Question('12A', 'Capital City of France', 'Paris')
            print('Exited setUp')
        
        def test_position_setter(self):
            square, direction = self.valid_question.key
            self.assertTupleEqual((12, 'A'), (square, direction))
        
        def test_position_setter_validation(self):
            with self.assertRaises(ValueError):
                self.valid_question.key = '10AB'
        
    unittest.main()