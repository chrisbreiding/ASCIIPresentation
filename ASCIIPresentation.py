import sublime
import sublime_plugin
import re
from pyfiglet import Figlet


ws_and_text = re.compile(r"^(\s*)(.*)$")

def indent_text(indentation, text):
    lines = map(lambda line: indentation + line, text.split("\n"))
    return "\n".join(lines)

def separate_indentation_from_text(text):
    match = re.search(ws_and_text, text)
    return match.group(1), match.group(2)

def heading_text(font, text):
    indentation, text = separate_indentation_from_text(text)
    ascii_text = indent_text(indentation, Figlet(font=font).renderText(text))

    return """##
%s
##
""" % ascii_text

def region_extended_back(region):
    return sublime.Region(region.begin() - 1, region.end())

def region_extended_back_has_line_break(view, region):
    if region.begin() <= 0:
        return True
    return re.search("\n", view.substr(region_extended_back(region)))

def text_extended_to_line_beginning(view, region):
    text = view.substr(region)
    no_line_break = not region_extended_back_has_line_break(view, region)

    while no_line_break:
        region = region_extended_back(region)
        view.sel().subtract(region)
        view.sel().add(region)
        text = view.substr(region)
        no_line_break = not region_extended_back_has_line_break(view, region)

    return text, region

def convert_title(view, edit, font_setting):
    for region in reversed(view.sel()):
        if region.empty():
            region = view.word(region)
            view.sel().add(region)

        text, region = text_extended_to_line_beginning(view, region)
        font = sublime.load_settings('ASCIIPresentation.sublime-settings').get(font_setting)
        view.replace(edit, region, heading_text(font, text))


class ConvertTitleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        convert_title(self.view, edit, 'title_font')


class ConvertHeadingCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        convert_title(self.view, edit, 'heading_font')


class AddTerminalCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        pass


class NewSlideCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        pass
