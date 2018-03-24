"""
A trivia quiz where you have to answer the question before last.
"""
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.skills.audioservice import AudioService
from mycroft import adds_context
from mycroft.util.log import LOG
import os, json, random
import MycroftDisplay.utils, MycroftDisplay.Mark1

GRID = MycroftDisplay.utils.normalise_grid("""

        .##.........................##..
        ##..#.#.#.#.#.#.#.#.#.#.#.#..##.
        .##.........................##..
        ................................
        ................................
        ................................
        ................................
        ................................
""")

CROSS = MycroftDisplay.utils.normalise_grid("""

        #######
        #..#..#
        ##...##
        #..#..#
        #######
""")


class OneBeforeLastSkill(MycroftSkill):
    def __init__(self):
        super(OneBeforeLastSkill, self).__init__(name="OneBeforeLastSkill")
        self.answer_index = 0
        self.question_index = 0
        self.wrong = 0

    def initialize(self):
        self.audio_service = AudioService(self.emitter)
        self.set_visual()

    @intent_handler(IntentBuilder("StartupIntent").require("Startup"))
    @adds_context("IsPlaying")
    def startup_intent(self, message):
        self.speak_dialog("welcome")
        fp = open(os.path.join(os.path.split(__file__)[0], "tfqdb.json"))
        self.questions = json.load(fp)
        fp.close()
        random.shuffle(self.questions)
        self.questions = self.questions[:4]
        self.speak_dialog("first.question.intro")
        self.speak_dialog("question", data={"question": self.questions[0]["question"], "index": 1})
        self.speak_dialog("second.question.intro")
        self.speak_dialog("question", data={"question": self.questions[1]["question"], "index": 2})
        self.speak_dialog("second.question.ask", expect_response=True)
        self.answer_index = 0
        self.question_index = 1

    @intent_handler(IntentBuilder("RepeatIntent").require("Repeat"))
    @adds_context("IsPlaying")
    def repeat_intent(self, message):
        self.speak_dialog("question", 
            data={"question": self.questions[self.question_index]["question"], "index": self.question_index+1},
            expect_response=True)

    @intent_handler(IntentBuilder("AnsweredTrueIntent").require("True").require("IsPlaying"))
    def answer_true_intent(self, message):
        self.handle_answer(expected=True)

    @intent_handler(IntentBuilder("AnsweredFalseIntent").require("False").require("IsPlaying"))
    def answer_false_intent(self, message):
        self.handle_answer(expected=False)

    def handle_answer(self, expected):
        if self.questions[self.answer_index]["answer"] == expected:
            # correct!
            self.play_sound("correct.mp3")
            self.speak_dialog("correct")
            self.set_visual()
            self.question_index += 1
            self.answer_index += 1
            if self.question_index == len(self.questions):
                self.speak_dialog("final.answer", expect_response=True)
            elif self.question_index > len(self.questions):
                self.play_sound("win.mp3")
                self.speak_dialog("complete")
            else:
                self.speak_dialog("question", 
                    data={"question": self.questions[self.question_index]["question"], "index": self.question_index+1},
                    expect_response=True)
        else:
            # wrong!
            self.wrong += 1
            self.set_visual()
            if self.wrong == 3:
                self.fail()
                return
            self.play_sound("wrong.mp3")
            self.speak_dialog("wrong", data={"count": self.wrong})
            self.question_index = 1
            self.answer_index = 0
            self.speak_dialog("question", 
                data={"question": self.questions[0]["question"], "index": 1})
            self.speak_dialog("question", 
                data={"question": self.questions[1]["question"], "index": 2})
            self.speak_dialog("second.question.ask", expect_response=True)

    def fail(self):
        self.play_sound("failure.mp3")
        self.speak_dialog("fail")

    def play_sound(self, sound):
        self.audio_service.play(os.path.join(os.path.split(__file__)[0], "sounds", sound))

    def stop(self):
        self.stop_requested = True
        return False

    def set_visual(self):
        g = GRID[:]
        for i in range(self.answer_index):
            g = MycroftDisplay.utils.insert_grid(g, "#", 4+(i*2), 1)
        for i in range(self.wrong):
            g = MycroftDisplay.utils.insert_grid(g, CROSS, 4+(i*8), 3)
        for img_code, x, y in MycroftDisplay.Mark1.from_large_grid(g):
            self.enclosure.mouth_display(img_code=img_code, x=x, y=y)


def create_skill():
    return OneBeforeLastSkill()
