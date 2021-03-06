'''
Created on 4 Dec 2013

@author: davesnowdon
'''
import unittest
import json

from translators.json.core import JsonTranslator
from testutil import make_joint_dict, POSITION_ZERO, POSITION_ARMS_UP, POSITION_ARMS_OUT, POSITION_ARMS_DOWN, POSITION_ARMS_BACK, POSITION_ARMS_RIGHT_UP_LEFT_OUT, POSITION_ARMS_LEFT_UP_RIGHT_OUT, POSITION_ARMS_LEFT_FORWARD_RIGHT_DOWN, POSITION_ARMS_RIGHT_FORWARD_LEFT_DOWN, POSITION_ARMS_RIGHT_DOWN_LEFT_BACK, POSITION_ARMS_LEFT_DOWN_RIGHT_BACK, POSITION_HANDS_CLOSE, POSITION_HANDS_OPEN, POSITION_HANDS_RIGHT_OPEN_LEFT_CLOSE, POSITION_HANDS_LEFT_OPEN_RIGHT_CLOSE, POSITION_ELBOWS_STRAIGHT_TURN_IN, POSITION_ELBOWS_BENT_TURN_UP, POSITION_ELBOWS_STRAIGHT_TURN_DOWN, POSITION_WRISTS_CENTER, POSITION_WRISTS_TURN_IN, POSITION_WRISTS_TURN_OUT, POSITION_WRISTS_RIGHT_CENTER_LEFT_TURN_OUT, POSITION_WRISTS_RIGHT_TURN_IN_LEFT_CENTER, POSITION_HEAD_DOWN_HEAD_FORWARD, POSITION_HEAD_UP_HEAD_RIGHT, POSITION_HEAD_CENTER_HEAD_LEFT

def get_translator():
    return JsonTranslator()

class TestGenerate(unittest.TestCase):
    def testEmptyList(self):
        result = get_translator().generate(set(), set(), set())
        # print "empty command result = {}".format(result)
        self.assertEqual("", result, "Empty commands should yield empty string")

    def testOneCommand(self):
        joint_dict = { "HeadPitch" : 0 }
        changed_joints = set(["HeadPitch"])
        result = get_translator().generate(joint_dict, changed_joints, changed_joints)
        # print "one command result = {}".format(result)
        result_obj = json.loads(result)
        self.assertEqual(0, result_obj["changes"]["HeadPitch"],
                         "HeadPitch joint should be in JSON")

    def testTwoCommands(self):
        joint_dict = { "HeadPitch" : 0,
                       "HeadYaw" : 0 }
        changed_joints = set(["HeadPitch", "HeadYaw"])
        result = get_translator().generate(joint_dict, changed_joints, changed_joints)
        result_obj = json.loads(result)
        # print "two command result = {}".format(result)
        self.assertEqual(2, len(result_obj["changes"]),
                         "Two commands should yield 2 changed joint anbles")

    def testKeyframeWithDuration(self):
        joint_dict = { "HeadPitch" : 0,
                       "HeadYaw" : 0 }
        changed_joints = set(["HeadPitch", "HeadYaw"])
        result = get_translator().generate(joint_dict, changed_joints, changed_joints,
                                           is_blocking=True, keyframe_duration=1.0)
        result_obj = json.loads(result)
        # print "two command result = {}".format(result)
        self.assertEqual(1.0, result_obj["duration"], "Command should include duration")
        self.assertEqual(True, result_obj["is_blocking"], "Command should be blocking")

    def testNoCommandsithDuration(self):
        commands = []
        result = get_translator().generate(set(), set(), set(), is_blocking=True, fluentnao="nao.",
                                                   keyframe_duration=1.0)
        self.assertEqual("", result, "empty command list should generate empty string even with duration")


class TestAppendCommands(unittest.TestCase):
    def testAppendEmptytoEmpty(self):
        result = get_translator().append('', '')
        self.assertEqual("", result, "appending empty to empty should be empty")

    def testAppendEmptyToCommand(self):
        cmd = '{ "is_blocking" : true }'
        result = get_translator().append(cmd, '')
        try:
            json.loads(result)
        except ValueError as e:
            self.fail("result '{}' should be valid JSON: {}".format(result, e))
        self.assertEqual(cmd.strip(), result.strip(),
                         "appending empty string should not change command apart from leading and trailing whitespace")

    def testAppendCommandToEmpty(self):
        cmd = '{ "is_blocking" : true }'
        result = get_translator().append('', cmd)
        try:
            json.loads(result)
        except ValueError as e:
            self.fail("result '{}' should be valid JSON: {}".format(result, e))
        self.assertEqual("[\r\n{}\r\n]".format(cmd), result.strip(),
                         "single command shoud be enclosed by square brackets")

    def testAppendCommandToCommand(self):
        code = '[\r\n{ "HeadPitch" : 0, "HeadYaw" : 0 }\r\n]'
        cmd = '{ "is_blocking" : true }'
        result = get_translator().append(code, cmd)
        try:
            result_obj = json.loads(result)
            self.assertEqual(2, len(result_obj), "should be 2 commands")
        except ValueError as e:
            self.fail("result '{}' should be valid JSON: {}".format(result, e))

    def testAppendCommandToMultipleCommands(self):
        code = '[{ "HeadPitch" : 0, "HeadYaw" : 0 }, { "HeadPitch" : 0, "HeadYaw" : 0 }]'
        cmd = '{ "is_blocking" : true }'
        result = get_translator().append(code, cmd)
        try:
            result_obj = json.loads(result)
            self.assertEqual(3, len(result_obj), "should be 3 commands")
        except ValueError as e:
            self.fail("result '{}' should be valid JSON: {}".format(result, e))


class TestReversible(unittest.TestCase):
    def testIsRevsible(self):
        self.assertTrue(get_translator().is_reversible, "JSON translator should be reversible")

    def testReversible(self):
        code = '''
        [
        {"duration": 1.0, "is_blocking": true, "changes": {"RShoulderPitch": 1.1658821105957031}},
        {"duration": 1.0, "is_blocking": true, "changes": {"RShoulderPitch": 1.1137261390686035}},
        {"duration": 1.0, "is_blocking": true, "changes": {"RShoulderPitch": 1.0600361824035645}}
        ]
        '''
        try:
            result_obj = get_translator().parse(code)
            self.assertEqual(3, len(result_obj), "Parsed result should contain 3 commands")
        except:
            self.fail("Parsing commands failed")
