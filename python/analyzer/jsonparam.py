# -*- coding: utf-8 -*-

import json
import logging

from jsonschema import validate
from jsonschema.exceptions import ValidationError


SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "definitions": {
        "software_task": {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"]
        },
        "hardware_task_argument": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "mode": {
                    "type": "string",
                    "enum": ["axis", "m_axi", "s_axilite"]
                },
                "offset": {"type": "string"},
                "bundle": {"type": "string"},
                "direction": {"type": "string"},
                "num": {"type": "string"}
            },
            "required": ["name", "mode", "num"]
        },
        "hardware_task_bundle": {
            "type": "object",
            "properties": {
                "bundle": {"type": "string"},
                "port": {"type": "string"}
            },
        },
        "hardware_task": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "mode": {
                    "type": "string",
                    "enum": ["s_axilite"]
                },
                "arguments": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/hardware_task_argument"}
                },
                "bundles": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/hardware_task_bundle"}
                }
            },
            "required": ["name", "arguments"]
        },
        "environments": {
            "type": "object",
            "properties": {
                "vendor": {"type": "string"},
                "board": {"type": "string"},
                "ostype": {"type": "string"}
            },
        },
    },
    "type": "object",
    "properties": {
        "software_tasks": {
            "type": "array",
            "items": {"$ref": "#/definitions/software_task"}
        },
        "hardware_tasks": {
            "type": "array",
            "items": {"$ref": "#/definitions/hardware_task"}
        },
        "environments": {
            "type": "object",
            "items": {"$ref": "#/definitions/environments"}
        }
    },
    "required": ["software_tasks", "hardware_tasks"]
}


class Task(object):
    def __init__(self, name):
        self.name = name

class SoftwareTask(Task):
    @staticmethod
    def parse_config(node):
        return SoftwareTask(node["name"])

class HardwareTask(Task):
    def __init__(self, name, mode, arguments, bundles):
        super(HardwareTask, self).__init__(name)
        self.mode = mode
        self.arguments = arguments
        self.bundles = bundles

    @staticmethod
    def parse_config(node):
        name = node["name"]
        mode = node.get("mode")
        arguments = [HardwareTaskArgument.parse_config(n)
                     for n in node["arguments"]]
        bundles = [HardwareTaskBundle.parse_config(n)
                     for n in node["bundles"]]

        return HardwareTask(name, mode, arguments, bundles)


class HardwareTaskArgument(object):
    def __init__(self, name, mode, offset=None, bundle=None,
            direction=None, num=None):
        self.name = name
        self.mode = mode
        self.offset = offset
        self.bundle = bundle
        self.direction = direction
        self.num = num

    @staticmethod
    def parse_config(node):
        name = node["name"]
        mode = node["mode"]
        offset = node.get("offset")
        bundle = node.get("bundle")
        direction = node.get("direction")
        num = node["num"]
        return HardwareTaskArgument(name, mode, offset, bundle, direction, num)


class HardwareTaskBundle(object):
    def __init__(self, bundle=None, port=None):
        self.bundle = bundle
        self.port = port

    @staticmethod
    def parse_config(node):
        bundle = node.get("bundle")
        port = node.get("port")
        return HardwareTaskBundle(bundle, port)


class TasksConfig(object):
    def __init__(self, hardware_tasks, software_tasks, environments):
        self.hardware_tasks = hardware_tasks
        self.software_tasks = software_tasks
        self.environments = environments

    def hw_funcname(self, config):
        # TODO: Currently we support only 1 HWtask
        functions = config.hardware_tasks.keys()
        if len(functions):
            return str(functions[0])
        else:
            return None

    def vendorname(self, config):
        vendor_name = "xilinx"
        if "vendor" in config.environments:
            return config.environments["vendor"]
        else:
            return vendor_name

    def boardname(self, config):
        board_name = "zedboard"
        if "board" in config.environments:
            return config.environments["board"]
        else:
            return board_name


    @staticmethod
    def parse_config(filename):
        with open(filename) as f:
            root = json.load(f)
            try:
                validate(root, SCHEMA)
            except ValidationError as e:
                logging.error("config validation error: %s", e)
                return None

        hw_tasks = {}
        sw_tasks = {}
        environments = {}

        for node in root["hardware_tasks"]:
            task = HardwareTask.parse_config(node)
            hw_tasks[task.name] = task

        for node in root["software_tasks"]:
            task = SoftwareTask.parse_config(node)
            sw_tasks[task.name] = task

        environments.update(root["environments"])

        return TasksConfig(hw_tasks, sw_tasks, environments)
