# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import requests 
import base64
import random
import json

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import requests 
import random
import urllib
# QUESTIONS = [['Which of the following authors was not born in England? ', 'D', ['Graham Greene', 'H G Wells', 'Arthur C Clarke', 'Arthur Conan Doyle']], ['When Halo 3: ODST was unveiled in 2008, it had a different title. What was the game formally called?', 'B', ['Halo 3: Helljumpers', 'Halo 3: Recon', 'Halo 3: Phantom', 'Halo 3: Guerilla']], ["What word represents the letter 'T' in the NATO phonetic alphabet?", 'C', ['Target', 'Taxi', 'Tango', 'Turkey']], ['What is the real name of Canadian electronic music producer deadmau5?', 'A', ['Joel Zimmerman', 'Sonny Moore', 'Adam Richard Wiles', 'Thomas Wesley Pentz']], ['In the programming language "Python", which of these statements would display the string "Hello World" correctly?', 'B', ['console.log("Hello World")', 'print("Hello World")', 'echo "Hello World"', 'printf("Hello World")']], ['Which female player won the gold medal of table tennis singles in 2016 Olympics Games?', 'D', ['LI Xiaoxia (China)', 'Ai FUKUHARA (Japan)', 'Song KIM (North Korea)', 'DING Ning (China)']], ['What is the smallest country in the world?', 'D', ['Maldives', 'Monaco', 'Malta', 'Vatican City']], ['What is the last name of the primary female protagonist of Final Fantasy VIII?', 'B', ['Loire', 'Heartilly', 'Almasy', 'Trepe']], ["The 'In the Flesh' tour was used in support of what Pink Floyd album?", 'A', ['Animals', 'The Wall', 'Wish You Were Here', 'The Final Cut']], ['What is the star sign of someone born on Valentines day?', 'C', ['Pisces', 'Capricorn', 'Aquarius', 'Scorpio']]]

def decode(s):
    d = urllib.parse.parse_qs(s, True).keys()
    return list(d)[0]


def get_questions(n = 10):  
    index_to_letter = {
        0:'A',
        1:'B',
        2:'C',
        3:'D'
    }
    questions = []
    # api-endpoint 
    URL = "https://opentdb.com/api.php?"
      
    PARAMS = {'amount': n,
              'type' : 'multiple'
              ,'encode':'url3986' # url3986 because it bugs out on the default encoding
             } 
    
    # sending get request and saving the response as response object 
    r = requests.get(url = URL, params = PARAMS) 

    # extracting data in json format 
    data = r.json()

    # checking the response worked
    if data['response_code']!= 0:
        #do something
        print('yikes')
    else:
        # decode the questions and answers, put them in a dict
        for q in data['results']:
            enunciate = decode(q['question'])
            correct = decode(q['correct_answer'])
            options = []
            for inc in q['incorrect_answers']:
                options.append(decode(inc))
            
            # insert the correct answer in a random position in the option array
            index = random.randint(0, len(options))
            options.insert(index, correct)
            print(correct, index)

            questions += [[enunciate, index_to_letter[index] , options]]

    return questions

def get_current_question(questions, n):
    return questions[n][0]

def get_current_answer(questions, n):
    return questions[n][1]

def get_current_options(questions, n):
    s = ""
    letters = ["A", "B", "C", "D", "E", "F"]
    for index, option in enumerate(questions[n][2]):
        s += ("%s - %s. \n" % (letters[index], option) )
    return s

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello there, welcome to Quiz Duel! \nAre you playing solo or multiplayer?"
        reprompt = "Playing by yourself (solo) or with a friend (miltiplayer)?"
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["questions"] = []
        session_attr["current_question"] = 0
        session_attr["last_speech"] = speak_output
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt)
                .response
        )
class GameModeIntentHandler(AbstractRequestHandler):
    """Handler for Game mode Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GameModeIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        mode = slots["Mode"].value

        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["mode"] = mode
        if mode == "solo":
            session_attr["points"] = 0
        else:
            session_attr["points_p1"] = 0
            session_attr["points_p2"] = 0
            session_attr["curr_player"] = 1

        speak_output = "How many questions do you want to play?" 
        session_attr["last_speech"] = speak_output
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class QuestionIntentHandler(AbstractRequestHandler):
    """Handler for (number of) Questions Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("QuestionIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        session_attr = handler_input.attributes_manager.session_attributes
        n = int(slots["questions"].value)
        if "mode" not in session_attr:
            return (
                handler_input.response_builder
                    .speak("Please select a game mode")
                    .ask("Please select a game mode")
                    .response
            )
        if (session_attr["mode"] == "solo" and n > 50) or (session_attr["mode"] != "solo" and n > 25):
            return (
            handler_input.response_builder
                .speak("You can only play up to 50 questions for solo and 25 questions for multiplayer at a time, please choose a smaller number")
                .ask("You can only play up to 50 questions for solo and 25 questions for multiplayer at a time, please choose a smaller number")
                .response
            )

        speak_output = "Okay, getting " +  str(n)
        if n > 1:
            speak_output += " questions"
        else:
            speak_output += " question"

        if  session_attr["mode"] != "solo":
            n *= 2
            speak_output += " for each player. First question for player 1: "
        else:
            speak_output += ". First question: "

        session_attr["questions"] = get_questions(n)
        session_attr["number_of_questions"] = n
        current_question = session_attr["current_question"]

        quest =  get_current_question(session_attr["questions"], current_question)
        quest += " Options: " +  get_current_options(session_attr["questions"], current_question)

        speak_output += quest
        session_attr["last_speech"] = speak_output
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(quest)
                .response
        )

class AnswerIntentHandler(AbstractRequestHandler):
    """Handler for Answer Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AnswerIntent")(handler_input) or
                 ask_utils.is_intent_name("DontKnowIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        letter_to_index = {
            'A':0,
            'B':1,
            'C':2,
            'D':3
        }
        
        session_attr = handler_input.attributes_manager.session_attributes
        questions = session_attr["questions"]
        mode = session_attr["mode"]
        correct_answer = get_current_answer(questions, session_attr["current_question"])

        intent_name = ask_utils.get_intent_name(handler_input)
        if intent_name == "AnswerIntent":
            slots = handler_input.request_envelope.request.intent.slots
            answer = slots["Answer"].value
            if answer.lower()[0] == correct_answer.lower():
                if mode == "solo":
                    session_attr["points"] += 1
                else:
                    if session_attr["curr_player"] == 1:
                        session_attr["points_p1"] += 1
                    else:    
                        session_attr["points_p2"] += 1
                    
                speak_output = "Correct! "
            
            else:
                answer_text = get_correct_answer_text(questions, session_attr["current_question"], letter_to_index[correct_answer])
                speak_output = ("Incorrect, the answer was %s - %s. "  % (correct_answer, answer_text))      
        else:
            answer_text = get_correct_answer_text(questions, session_attr["current_question"], letter_to_index[correct_answer])     
            speak_output = ("That's ok! the answer was %s - %s. "  % (correct_answer, answer_text))
            
        session_attr["current_question"] += 1
        if mode == "multiplayer":
            session_attr["curr_player"] = 2 if session_attr["curr_player"] == 1 else 1
                
        
        if session_attr["current_question"] >= session_attr["number_of_questions"]:
            speak_output += "Thanks for playing! "
            if mode == "solo":
                speak_output += ("Final score: %s. " % getPointsString(session_attr["points"]))
            else:
                if session_attr["points_p1"] == session_attr["points_p2"]:
                    speak_output += ("It's a tie! Amazing! You both have %s. " % getPointsString(session_attr["points_p1"]))
                else:
                    if session_attr["points_p1"] > session_attr["points_p2"]:
                        winner = 1
                        loser = 2
                        pointsW = getPointsString(session_attr["points_p1"])  
                        pointsL = getPointsString(session_attr["points_p2"])
                    else:
                        winner = 2
                        loser = 1
                        pointsW = getPointsString(session_attr["points_p2"])
                        pointsL = getPointsString(session_attr["points_p1"])  

                    speak_output += ("Congratulations player %d! You won with %s. Player %d got %s, better luck next time!" % (winner, pointsW, loser, pointsL))
            
            session_attr["last_speech"] = speak_output
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .set_should_end_session(True)
                    .response
            )
        else:
            if mode != "solo":
                speak_output += ("For player %d, " % session_attr["curr_player"])
                question_number = (session_attr["current_question"] + 2) // 2
            else:
                question_number = (session_attr["current_question"] + 1) 
            question = get_current_question(questions, session_attr["current_question"]) + " Options: " + get_current_options(questions, session_attr["current_question"])
            
            speak_output += ("question number %d: %s" %(question_number, question))
            reprompt = "Sorry, I didnt get that. Here is your question again: " + question
            session_attr["last_speech"] = speak_output
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(reprompt)
                    .response
            )

def getPointsString(n):
    return str(n) + " points" if n != 1 else str(n) + " point"
def get_correct_answer_text(questions, q, n):
    return questions[q][2][n]

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = """A general knowledge quiz. There are 2 modes: solo, for playing alone, or multiplayer, for playing with a friend. 
                          You can play up to 50 questions at a time!"""
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["last_speech"] = speak_output
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye, hope to see you again soon!" # :)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response

class RepeatIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.RepeatIntent")(handler_input)

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        speak_output = session_attr["last_speech"] 
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Oops, I had trouble doing what you asked. Please try again. " + str(exception)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(QuestionIntentHandler())
sb.add_request_handler(AnswerIntentHandler())
sb.add_request_handler(GameModeIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(RepeatIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()