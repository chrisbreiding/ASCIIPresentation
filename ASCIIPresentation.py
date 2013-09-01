import sublime
import sublime_plugin
from pyfiglet import Figlet


def heading_text(font, text):
    return """##
%s
##""" % Figlet(font=font).renderText(text)


def convert_title(view, edit, font_setting):
    for region in reversed(view.sel()):
        # if no selection, use the current word
        if region.empty():
            region = view.word(region)

        text = view.substr(region)
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
