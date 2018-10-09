from .board import Board
from .question import Question
from .filedb import FileDB
from .clear_screen import clear


class CLI():

    def __init__(self, database):
        self.database = database
        self.__crosswords = self.database.read_all()
        clear()

    def run(self):
        """ Initiates the user interface. """
        welcome_msg = 'Welcome to Crossword Program'
        line = '='*len(welcome_msg)
        print(line)
        print(welcome_msg)
        print(line)
        
        def choose_mode():
            """ Displays a menu of options to the user and selects an operation based on their input. """
            user_input = ''
            self.__display_information('\nMENU\n____\n')

            def get_mode():
                print('-> Play crossword (P)')
                print('-> Create new crossword (C)')
                print('-> Edit Crossword (E)')
                print('-> Quit (Q)')
                print('')
                return input('>>  ').upper()

            user_input = get_mode()

            while user_input != 'C' and user_input != 'P' and user_input!= 'Q' and user_input != 'E':
                self.__display_error('\nInvalid option. Please try again.\n')
                user_input = get_mode()
            
            if user_input == 'P':
                clear()
                self.__play()
                choose_mode()
            elif user_input == 'C':
                clear()
                self.__create_crossword()
                choose_mode()
            elif user_input == 'E':
                self.__edit()
                choose_mode()
            else:
                self.__quit_program()
        
        choose_mode()
    
            
    def __quit_program(self):
        """ Exits the program. """
        print('\nGoodbye!')
    
    def __play(self):
        """ Enters the play operation. """
        if len(self.__crosswords) == 0:
            self.__display_error('No crosswords in the database please add one to play.')
        else:
            continue_playing = True
            while continue_playing:
                unplayed_crosswords = filter(lambda xword: xword.played == False, self.__crosswords)
                try:
                    continue_playing = self.__play_crossword(next(unplayed_crosswords))
                except StopIteration:
                    play_old_crossword = self.__get_boolean_input_from_user('No unplayed crosswords remain. Would you like to play an old one?')
                    if play_old_crossword:
                        previously_played_crosswords = iter(self.__crosswords)
                        crossword = next(previously_played_crosswords)
                        crossword.reset_guesses()
                        continue_playing = self.__play_crossword(crossword)
                    else:
                        continue_playing = False
            self.database.save(self.__crosswords)


    def __play_crossword(self, crossword):
        """ Play a crossword.

        Args:
            crossword: the crossword object to be played.
        
        Returns:
            Boolean: True if the user wishes to remain in play mode.

        """
        crossword.played = True
        crossword.print_guesses_board()
        crossword.print_questions()
        user_input = ''
        crossword_complete = False
        while user_input != '-1' and not crossword_complete:
            user_input = input('\nEnter the question key followed by your guess.\n>\t')
            if user_input == '-1': continue
            elif user_input == 'check':
                clear()
                crossword.print_guesses_board(check=True)
                crossword.print_questions()
                continue
            else:
                try:
                    key, guess = user_input.split(' ')
                    crossword.make_guess(key.upper(), guess)
                    crossword_complete = crossword.is_complete()
                    if crossword_complete:
                        self.__display_information('All questions answered.')
                        incorrect_squares = crossword.check_guesses()
                        if incorrect_squares == 0:
                            self.__display_success('Congratulations you completed the crossword correctly.')
                        else:
                            crossword.print_guesses_board(check=True)
                            self.__display_error('Oh no! There are {} incorrect squares.'.format(incorrect_squares))
                            crossword_complete = False
                            crossword.print_questions()
                    else:
                        clear()
                        crossword.print_guesses_board()
                        crossword.print_questions()
                except ValueError as err:
                    self.__display_error(str(err))
                    continue
                except KeyError as err:
                    self.__display_error(str(err))
                    continue
        continue_playing = input('Would you like to play again? (y/n) ').upper() == 'Y'
        clear()
        return continue_playing


    def __get_boolean_input_from_user(self, message):
        """ Gets a Boolean response from the user in response to a message.

        Args:
            message: The message to be displayed to the user.
        
        Returns:
            Boolean: True if user selects 'y', False if user selects 'n'
        """
        try:
            user_input = input("{}: (y\\n) ".format(message)).upper()
            if user_input != 'Y' and user_input != 'N':
                raise ValueError()
            else: return user_input == 'Y'
        except ValueError:
            self.__display_error('Invalid input. Please try again.')
            return self.__get_boolean_input_from_user(message)


    def __create_crossword(self):
        """ Create a crossword """
        self.__display_information('Create a new Crossword.')

        def get_dimension(metric):
            """ Gets an integer value from the user for a specified metric.

            Args:
                metric: The name of the integer dimension the user is to input
            
            Returns:
                Integer: The int value for the str input from the user.
            """
            try:
                value = int(input('{}:  '.format(metric)))
                return value
            except ValueError:
                self.__display_error('Oops! Value must be an integer. Try again!')
                return get_dimension(metric)
                
        height = get_dimension('Number of squares high')
        width = get_dimension('Number of squares across')
        crossword = Board(width=width, height=height)

        def getQuestion():
            """ Gets data from user to create Question object.

            Returns:
                Question: A Question object representing the values the user has entered.
            """
            try:
                question = Question('1A', '', '')
                key = input('Question Key:  ')
                question.key = key
                text = input('Question:  ')
                question.text = text
                answer = input('Answer:  ')
                question.answer = answer
                return question
            except ValueError as err:
                self.__display_error('Oops, ' + str(err))
                return getQuestion()

        add_question = self.__get_boolean_input_from_user('Add question? ')
        while add_question:
            question = getQuestion()
            pos_x = get_dimension('Column')
            pos_y = get_dimension('Row')
            try:
                crossword.add_question(question, x=pos_x, y=pos_y)
                clear()
                crossword.print_answers_board()
                self.__display_success('Question added!')
                add_question = self.__get_boolean_input_from_user('Add another question?')
            except ValueError as err:
                self.__display_error('Cannot add that question. ' + str(err))
                self.__display_error('Please try again.')

        
        def save_crossword(crossword):
            """ Save the crossword to the database """
            self.__crosswords.append(crossword)
            self.database.create(self.__crosswords)
            self.__display_success('Crossword Saved!')
            
        def get_confirmation():
            """ Gets confirmation from the user if the wish to discard a crossword. """
            should_save = self.__get_boolean_input_from_user('Save crossword?')
            if should_save:
                save_crossword(crossword)
            else:
                confirm_discard = self.__get_boolean_input_from_user('Are you sure you want to discard this crossword?')
                if not confirm_discard:
                    save_crossword(crossword)
                else:
                    self.__display_information('Crossword discarded.')
             
        get_confirmation()
    
    def __edit(self):
        self.__display_information('EDIT\n______')
        print('Select a crossword to edit')
        for index,xword in enumerate(self.__crosswords):
            print("{} {}".format(index, xword))
        
        def get_crossword_to_edit():
            try:
                number = int(input('Number: '))
                return self.__crosswords[number]
            except IndexError:
                self.__display_error('Invalid number! Please try again.')
                return get_crossword_to_edit()
            except ValueError:
                self.__display_error('Must be an integer. Please try again.')
                return get_crossword_to_edit()
        
        crossword_to_edit = get_crossword_to_edit()

        self.__edit_crossword(crossword_to_edit)
    
    def __edit_crossword(self, crossword):
        crossword.print_answers_board()
        crossword.print_questions()
        question_key = ''

        def edit_question(key):
            try:
                question = crossword.get_question(key)
                text = input('Question: ')
                answer = input('Answer: ')
                if text != '': question.text = text
                if answer != '': question.answer = answer
            except KeyError as err:
                self.__display_error(str(err) + ' Please try again.')

        while question_key != '-1':
            question_key = input('\nKey: ')
            if question_key == '-1': continue
            clear()
            edit_question(question_key)
            crossword.print_answers_board()
            crossword.print_questions()
        
        self.database.save(self.__crosswords)
        self.__display_success('Edit saved!')


    def __display_error(self, message):
        """ Prints message in red """
        print("\033[1;31m{}\033[0m".format(message))
    
    def __display_success(self, message):
        """ Prints message in green. """
        print("\033[1;32m{}\033[0m".format(message))

    def __display_information(self, message):
        """ Prints message in blue. """
        print("\033[1;34m{}\033[0m".format(message))


if __name__ == '__main__':

    import unittest
    from unittest import mock
    from io import StringIO

    class TestCLI(unittest.TestCase):

        def setUp(self):
            print('In test set up')
            filedb = FileDB('test.txt')
            self.cli = CLI(filedb)
        
        def test_get_boolean_input_from_user(self):
            with mock.patch('builtins.input', return_value='Y'):
                self.assertTrue(self.cli.__get_boolean_input_from_user('Did this work?'))

        # def test_create_crossword(self):
        #     self.main._Main__create_crossword()
        

    unittest.main()