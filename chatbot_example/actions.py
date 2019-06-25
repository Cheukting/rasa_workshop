# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message("Hello World!")
#
#         return []


from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

import re

import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from rasa_sdk.events import SlotSet
import webbrowser


class ExperienceForm(FormAction):
    """Form action to capture user experience"""

    def name(self):
        # type: () -> Text
        """Unique identifier of the form"""

        return "experience_form"

    @staticmethod
    def required_slots(tracker):
        # type: () -> List[Text]
        """A list of required slots that the form has to fill
           this form collect the feedback of the user experience"""

        return ["feedback"]

    def submit(self, dispatcher, tracker, domain):
        # type: (CollectingDispatcher, Tracker, Dict[Text, Any]) -> List[Dict]
        """Define what the form has to do
           after all required slots are filled
           basically it generate sentiment analysis
           using the user's feedback"""

        sid = SentimentIntensityAnalyzer()

        all_slots = tracker.slots
        for slot, value in all_slots.items():
            if slot in self.required_slots(tracker):
                res = sid.polarity_scores(value)
                score = res.pop('compound', None)
                classi, confidence = max(res.items(), key=lambda x: x[1])
                # classification of the feedback, could be pos, neg, or neu
                all_slots[slot+'_class'] = classi
                # sentiment score of the feedback, range form -1 to 1
                all_slots[slot+'_score'] = score

        return [SlotSet(slot, value) for slot, value in all_slots.items()]

    def slot_mappings(self):
        # type: () -> Dict[Text: Union[Dict, List[Dict]]]
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {"feedback": [self.from_text()]}

class ContactForm(FormAction):
    """Form action to capture contact details"""

    def name(self):
        # type: () -> Text
        """Unique identifier of the form"""

        return "contact_form"

    @staticmethod
    def required_slots(tracker):
        # type: () -> List[Text]
        """A list of required slots that the form has to fill"""

        return ["name", "email", "tel"]

    def submit(self, dispatcher, tracker, domain):
        # type: (CollectingDispatcher, Tracker, Dict[Text, Any]) -> List[Dict]
        """Define what the form has to do
           after all required slots are filled"""

        dispatcher.utter_template('utter_submit', tracker)

        return []

    def slot_mappings(self):
        # type: () -> Dict[Text: Union[Dict, List[Dict]]]
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {"name": [self.from_entity(entity="PERSON",
                                          intent="self_intro"),
                         self.from_text()],
                "email": [self.from_entity(entity="email"),
                          self.from_text()],
                "tel": [self.from_entity(entity="tel"),
                        self.from_text()]}

    @staticmethod
    def is_email(string: Text) -> bool:
        """Check if a string is valid email"""
        pattern = re.compile("[\w-]+@([\w-]+\.)+[\w-]+")
        return pattern.match(string)

    @staticmethod
    def is_tel(string: Text) -> bool:
        """Check if a string is valid email"""
        pattern_uk = re.compile("(0)([0-9][\s]*){10}")
        pattern_world = re.compile("^(00|\+)[\s]*[1-9]{1}([0-9][\s]*){9,16}$")
        return pattern_uk.match(string) or pattern_world.match(string)

    def validate_email(
         self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
        ) -> Optional[Text]:
        if self.is_email(value):
            return {"email": value}
        else:
            dispatcher.utter_template('utter_wrong_email', tracker)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"email": None}

    def validate_tel(
         self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
        ) -> Optional[Text]:
        if self.is_tel(value):
            return {"tel": value}
        else:
            dispatcher.utter_template('utter_wrong_tel', tracker)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"tel": None}


class ActionShowResult(Action):
    """open the html showing the result of the user survey"""
    def name(self):
        # type: () -> Text
        return "action_show_result"

    def run(self, dispatcher, tracker, domain):
        # type: (CollectingDispatcher, Tracker, Dict[Text, Any]) -> List[Dict[Text, Any]]

        result = tracker.slots
        name = result['name']
        if name is None:
            name = 'Anonymous'
        else:
            name = name + "'s"
        http_result =""""""
        for key, value in result.items():
            if key != 'requested_slot':
                http_result += """<p>{}: {}</p>""".format(key, value)

        # url of the server set up by result.py
        url = 'http://localhost:8080/?name={}&result={}'.format(name, http_result)
        webbrowser.open(url)

        return []
