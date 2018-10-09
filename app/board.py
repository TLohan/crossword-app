""" board.py """

from .question import Question, Orientation
from itertools import repeat, chain


class Board(object):
    """ Models the frame of the crossword.

    Args:
        width: the number of squares across.
        hright: the number of squares high.
    """

    def __init__(self, width=15, height=15):
        self.width = width
        self.height = height
        self.questions = []
        self.__key_to_question_dict = {}
        self.__guesses_board = [list(repeat('   ', width)) for line in range(height)]
        self.__answers_board = [list(repeat('   ', width)) for line in range(height)]
        self.played = False
    

    def get_guesses_board(self):
        return self.__guesses_board

    @property
    def played(self):
        """ True if played. False is not."""
        return self.__played
    
    @played.setter
    def played(self, flag):
        self.__played = flag

    def add_question(self, question, x, y):
        """ Adds a question to the crossword.

        Args:
            question: the question object to add to the Board.
            x: The 0 based indice representing the column.
            y: The 0 based indice representing the row.
        
        Throws:
            ValueError: If the question is unable to be entered onto the board at that position
                due to the answer not fitting or there being a conflict with an existing question.
        """
        if question.orientation == Orientation.ACROSS:
            if x + question.length() > self.width:
                raise ValueError('Answer will not fit the board')
        else:
            if y + question.length() > self.height:
                raise ValueError('Answer will not fit the board.')
        question.coordinates = x, y
        self.questions.append(question)
        self.__key_to_question_dict[question.key] = question
        for index, letter in enumerate(question.answer):
            if question.orientation == Orientation.ACROSS:
                pos_x = x + index
                pos_y = y
            else:
                pos_x = x
                pos_y = y + index
            current_letter = self.__answers_board[pos_y][pos_x].strip()
            if current_letter == '' or current_letter == letter.upper():
                self.__answers_board[pos_y][pos_x] = " {} ".format(letter.upper())
                if index == 0:
                    if len(str(question.key[0])) == 1: self.__guesses_board[pos_y][pos_x] = ' {}'.format(question.key)
                    else: self.__guesses_board[pos_y][pos_x] = "{}".format(question.key)
                else:
                    self.__guesses_board[pos_y][pos_x] = "???"
            else:
                raise(ValueError('The letter {} at square {}{} does not match new letter {}.'.format(current_letter, pos_x, pos_y, letter)))

    def get_question(self, key):
        """ Retrieves question object from the dictionary based on its key.

        Raises:
            KeyError: no such question.
        """
        question = self.__key_to_question_dict.get(key)
        if question == None:
            raise KeyError()
        return question

    def __print_board(self, board, check=False):
        """ Prints the board to the console.

        Args:
            board: the board to be printed
            check: True if the guesses should be checked.
        """
        print('\n')
        incorrect_blocks = 0
        line = u"\033[90m\u002B\u2014\u2014\u2014\033[0m"*(self.width)
        for index_y, row in enumerate(board):
            print(line)
            r = ''
            for index_x, letter in enumerate(row):
                r += '\033[90m|\033[0m'
                if letter == '###':
                    letter = '\033[90m' + letter + '\033[0m'
                elif len(letter.strip()) != 1 or letter == '???':
                    letter = '\033[94m' + letter + '\033[0m'
                else:
                    if not check:
                        letter = '\033[95m' + letter + '\033[0m'
                    else:
                        if letter == self.__answers_board[index_y][index_x]:
                            # letter is right
                            letter = '\033[1;32m' + letter + '\033[0m'
                        else:
                            # letter is wrong
                            #print('wring!')
                            letter = '\033[1;31m' + letter + '\033[0m'
                            incorrect_blocks += 1
                r += letter
            r += "\033[90m|\033[0m"            
            print(r)
        print(line)
        return incorrect_blocks

    def reset_guesses(self):
        """ Resets the guesses made during a previous attempt. """
        for question in self.questions:
            for index in range(len(question.answer)):
                if question.orientation == Orientation.ACROSS:
                    pos_x = question.coord_x + index
                    pos_y = question.coord_y
                else:
                    pos_x = question.coord_x
                    pos_y = question.coord_y + index
                if index == 0:
                    if len(str(question.key[0])) == 1: self.__guesses_board[pos_y][pos_x] = ' {}'.format(question.key)
                    else: self.__guesses_board[pos_y][pos_x] = '{}'.format(question.key)
                else:
                    self.__guesses_board[pos_y][pos_x] = "???"
                
    def is_complete(self):
        """ Checks if an attempt has been made on all the questions. """
        question_guesses = [q.guessed for q in self.questions]
        return all(question_guesses)
    
    def check_guesses(self):
        """ Checks the guesses board against the answers board.

        Returns: 
            integer: the number of incorrect squares.
        """
        incorrect_squares = 0
        guesses = chain.from_iterable(self.__guesses_board)
        answers = chain.from_iterable(self.__answers_board)
        for guess, answer in zip(guesses, answers):
            if guess != answer:
                incorrect_squares += 1
        return incorrect_squares

    def print_questions(self):
        """ Prints the questions to the command line """
        max_question_length = max(map(lambda question: len(question.text), self.questions))
        questions_across = list(filter(lambda question: question.orientation == Orientation.ACROSS, self.questions))
        questions_down = list(filter(lambda question: question.orientation == Orientation.DOWN, self.questions))

        def format_question(question):
            """ Formats the question by whether it has been guessed or not """
            if question.guessed:
                return "\033[1;30m{}:\t{}  ({})\033[0m".format(question.key, question.text, question.length()) + " "*(max_question_length - len(question.text))
            else:
                return "\033[1;37m{}:\t{}  ({})\033[0m".format(question.key, question.text, question.length()) + " "*(max_question_length - len(question.text))

        for q_across,q_down in zip(questions_across, questions_down):
            print("{} \t {}".format(format_question(q_across), format_question(q_down)))



    def make_guess(self, key, guess):
        """ Adds a guess to a question.
        
        Args:
            key: the key to the question.
            guess: the guess.
        
        Raises:
            ValueError: The guess is longer than the answer.
            KeyError: No question matches that key.
        """
        try:
            question = self.get_question(key)
            if question.length() < len(guess): raise ValueError('Error!: Answer is too long!')
            question.guess = guess
            question.guessed = True
            for index, letter in enumerate(guess):
                letter = letter.upper()
                if question.orientation == Orientation.ACROSS:
                    pos_x = question.coordinates[0] + index
                    pos_y = question.coordinates[1]
                else:
                    pos_x = question.coordinates[0]
                    pos_y = question.coordinates[1] + index
                self.__guesses_board[pos_y][pos_x] = " {} ".format(letter)
        except KeyError:
            raise KeyError('Error: {} is not a valid question key!'.format(key))

    

    def print_guesses_board(self, check=False):
        """ Prints the guesses board. 
        
        Args:
            check: True if the guesses should be checked.
        """
        return self.__print_board(self.__guesses_board, check)
    
    def print_answers_board(self):
        """ Prints the answers board to the command line. """
        self.__print_board(self.__answers_board)

if __name__ == '__main__':
    import unittest
    import sys
    import io

    class TestBoard(unittest.TestCase):

        def setUp(self):
            self.valid_board = Board()
            self.valid_question = Question('12D', 'Capital City of France', 'Paris')
            self.valid_questions = [Question('8A', 'Commonplace', 'Ordinary'), Question('1D', 'Marcel ..., French novelist', 'proust'), Question('2D', 'On the board', 'Director'), Question('3D', 'Meal outside', 'Barbecue'),
                Question('10A', 'Surpassingly good', 'Superb'), Question('12A', 'Motionless', 'Static'), Question('17A', 'Barricade', 'Barrier')]
            self.coordinates = [(0,1), (1,0), (3, 0), (5, 0), (0, 3), (0, 5), (0, 7)]
        
        def test_add_invalid_question(self):
            with self.assertRaises(ValueError):
                self.valid_board.add_question(self.valid_question, 10, 12)
        
        def test_add_valid_question(self):
            self.valid_board.add_question(self.valid_question, 2, 0)
            self.assertEqual(self.valid_board.get_question('12D'), self.valid_question)
        
        def test_add_conflicting_question(self):
            self.valid_board.add_question(self.valid_question, 0, 0)
            conflicting_question = Question('1A', 'Capital City of Ireland', 'Dublin')
            with self.assertRaises(ValueError):
                self.valid_board.add_question(conflicting_question, 0, 0)

        # def test_print_board(self):
        #     self.valid_board.add_question(self.valid_question, 2, 0)
        #     self.valid_board.add_question(Question('3A', 'Capital City of Wales', 'Cardiff'), 0, 2)
        #     self.valid_board.print_guesses_board()
        #     self.valid_board.print_answers_board()
        
        # def test_make_guess(self):
        #     self.valid_board.add_question(self.valid_question, 2, 0)
        #     self.valid_board.add_question(Question('3A', 'Capital City of Wales', 'Cardiff'), 0, 2)
        #     self.valid_board.make_guess('12D', 'Paris')
        #     self.valid_board.print_guesses_board()
        
        def test_make_invalid_guess(self):
            self.valid_board.add_question(self.valid_question, 0, 0)
            with self.assertRaises(ValueError):
                self.valid_board.make_guess('12D', 'TooLong')

        # def test_print_questions(self):
        #     for coords, question in zip(self.coordinates, self.valid_questions):
        #         self.valid_board.add_question(question, coords[0], coords[1])
        #     self.valid_board.print_questions()
        

    
    unittest.main()