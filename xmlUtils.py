from enum import Enum
import re


class TagType(Enum):
    OPENING = "OPENING"
    CLOSING = "CLOSING"
    SINGLE = "SINGLE"
    TEXT = "TEXT"


xml_args_regex = r'\w+=\"[^\"]+\"'


def xml_args_to_obj(args):
    o = {}
    for arg in args:
        k, v = arg.split("=")
        o[k] = v.strip('"')
    return o


def getTagType(string):
    if string[:2] == "</":
        return TagType.CLOSING
    elif string[-2:] == "/>":
        return TagType.SINGLE
    else:
        return TagType.OPENING


class XMLTag():

    def __init__(self, raw_string):
        # string
        # isTag
        # tagType
        # tagName
        # tagProps
        self.string = raw_string
        self.isTag = (len(self.string) > 1 and self.string[0] == "<" and self.string[-1] == ">")
        if self.isTag:
            self.tagType = getTagType(self.string)
            self.tagName = self.string.strip("</>").split(" ")[0]
            self.tagProps = xml_args_to_obj(re.findall(xml_args_regex, self.string))
        else:
            self.tagType = TagType.TEXT
            self.tagName = "text"
            self.tagProps = {}


class TagListContentExtractor():
    empty_properties_gk = {
        "book": None,
        "chapter": None,
        "section": None,
        "quote": None,
        "source": None
    }

    empty_properties_eng = {
        "book": None,
        "chapter": None,
        "section": None,
        "quote": None,
        "source": None
    }

    empty_properties = {
        "gk": empty_properties_gk,
        "eng": empty_properties_eng
    }

    def __init__(self, tag_list):
        self.properties = {}
        self.reset_properties()
        self.tag_list = tag_list
        self.index = 0
        self.output = []
        self.skip = False
        self.stackingRows = False
        self.stackedRows = []

    def reset_properties(self, lang="gk"):
        self.properties = {**TagListContentExtractor.empty_properties[lang]}

    def set_property(self, key, value):
        self.properties[key] = value

    def push_to_output(self, string):
        self.output.append({**self.properties, "text": string})

    # def parse

    def parse_greek(self):
        self.index = 0
        self.reset_properties("gk")
        self.output = []
        self.skip = False
        self.stackingRows = False
        self.stackedRows = []

        for tag in self.tag_list:
            if tag.tagType == TagType.TEXT:
                if not self.skip:
                    if self.stackingRows:
                        self.stackedRows.append(tag.string)
                    else:
                        self.push_to_output(tag.string)
            else:
                if tag.tagName == "div1":
                    self.reset_properties("gk")
                    if tag.tagType == TagType.OPENING:
                        self.set_property(tag.tagProps["type"].lower(), tag.tagProps["n"])
                elif tag.tagName == "milestone" and tag.tagProps["unit"] != "para":
                    self.set_property(tag.tagProps["unit"], tag.tagProps["n"])
                elif tag.tagName == "quote":
                    if tag.tagType == TagType.OPENING:
                        self.set_property("quote", True)
                        self.stackingRows = True
                        if "type" in tag.tagProps:
                            self.set_property("quote", tag.tagProps["type"])
                    else:
                        self.push_to_output(" \n ".join(self.stackedRows))
                        self.set_property("quote", None)
                        self.stackingRows = False
                        self.stackedRows = []
                elif tag.tagName == "bibl":
                    if tag.tagType == TagType.OPENING:
                        source = tag.tagProps["n"]
                        self.output[-1]["source"] = source
                        self.skip = True
                    else:
                        self.skip = False
                else:
                    continue
        return self.output


    def parse_eng(self):
        self.index = 0
        self.reset_properties("eng")
        self.output = []
        self.skip = False
        self.stackingRows = False
        self.stackedRows = []

        for tag in self.tag_list:
            if tag.tagType == TagType.TEXT:
                if not self.skip:
                    if self.stackingRows:
                        self.stackedRows.append(tag.string)
                    else:
                        self.push_to_output(tag.string)
            else:
                if tag.tagName == "div1":
                    self.reset_properties("eng")
                    if tag.tagType == TagType.OPENING:
                        self.set_property(tag.tagProps["type"].lower(), tag.tagProps["n"])
                elif tag.tagName == "milestone" and tag.tagProps["unit"] != "para":
                    self.set_property(tag.tagProps["unit"], tag.tagProps["n"])
                elif tag.tagName == "quote":
                    if tag.tagType == TagType.OPENING:
                        self.set_property("quote", True)
                        self.stackingRows = True
                        if "type" in tag.tagProps:
                            self.set_property("quote", tag.tagProps["type"])
                    else:
                        self.push_to_output(" \n ".join(self.stackedRows))
                        self.set_property("quote", None)
                        self.stackingRows = False
                        self.stackedRows = []
                elif tag.tagName == "bibl":
                    if tag.tagType == TagType.OPENING:
                        source = tag.tagProps["n"]
                        self.output[-1]["source"] = source
                        self.skip = True
                    else:
                        self.skip = False
                else:
                    continue
        return self.output

    # pass
