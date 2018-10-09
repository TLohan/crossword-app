""" filedb.py """
import pickle
import os
class FileDB:
    """ Text file used to persist data 
    
    Args:
        filename: The path to the file.

    """

    def __init__(self, filename):
        if os.path.isfile(filename): 
            self.filename = filename
        else:
            raise FileNotFoundError('Error! Crosswords file does not exist!')

    def create(self, crosswords):
        """ Saves the a list of crosswords to the file.
        
        Args:
            crosswords: the list of crosswords
        """
        with open(self.filename, mode="wb") as file:
            pickle.dump(crosswords, file)
    
    def read_all(self):
        """ Reads all the crosswords from the file. """
        crosswords = []

        with open(self.filename, mode="rb") as file:
            try:
                crosswords = pickle.load(file)
            except EOFError:
                return crosswords
        return crosswords

    def save(self, crosswords):
        """ Saves the a list of crosswords to the file.
        
        Args:
            crosswords: the list of crosswords
        """
        with open(self.filename, mode="wb") as file:
            pickle.dump(crosswords, file)
    

if __name__ == '__main__':
    import unittest
    from .board import Board
    from .question import Question


    class TestFileDB(unittest.TestCase):

        def setUp(self):
            self.crosswords = []
            self.filedb = FileDB('test.txt')
            self.questions = [
                Question('1A', 'Capital City of Ireland.', 'Dublin'),
                Question('1D', "Copenhagen is it's capital city.", 'Denmark')
            ]
            self.coordinates = [[0,0], [0,0]]
            self.crosswordA = Board(15, 15)
            self.crosswordB = Board(14, 14)
            for question, coords in zip(self.questions, self.coordinates):
                self.crosswordA.add_question(question, x=coords[0], y=coords[1])
                self.crosswordB.add_question(question, x=coords[0], y=coords[1])
            self.crosswords= [self.crosswordA, self.crosswordB]
        
        def test_write(self):
            self.filedb.create(self.crosswords)

        def test_read_all(self):
            crosswords = self.filedb.read_all()
            print(len(crosswords))
            print(crosswords[0].questions)
    
    unittest.main()
        