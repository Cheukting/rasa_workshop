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


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from rasa.core.constants import REQUESTED_SLOT
from rasa_sdk.events import SlotSet

import re

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
                                            intent="self_intro")],
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

    def validate(self,
                 dispatcher: CollectingDispatcher,
                 tracker: Tracker,
                 domain: Dict[Text, Any]) -> List[Dict]:
        """Validate extracted requested slot
            else reject the execution of the form action
        """
        # extract other slots that were not requested
        # but set by corresponding entity
        slot_values = self.extract_other_slots(dispatcher, tracker, domain)

        # extract requested slot
        slot_to_fill = tracker.get_slot(REQUESTED_SLOT)
        if slot_to_fill:
            slot_values.update(self.extract_requested_slot(dispatcher,
                                                           tracker, domain))

        # we'll check when validation failed in order
        # to add appropriate utterances
        for slot, value in slot_values.items():
            if slot == 'email':
                if not self.is_email(value):
                    dispatcher.utter_template('utter_wrong_email', tracker)
                    # validation failed, set slot to None
                    slot_values[slot] = None

            elif slot == 'tel':
                if not self.is_tel(value):
                    dispatcher.utter_template('utter_wrong_tel', tracker)
                    # validation failed, set slot to None
                    slot_values[slot] = None

        # validation succeed, set the slots values to the extracted values
        return [SlotSet(slot, value) for slot, value in slot_values.items()]

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

        return []

    def slot_mappings(self):
        # type: () -> Dict[Text: Union[Dict, List[Dict]]]
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {"feedback": [self.from_text()]}
