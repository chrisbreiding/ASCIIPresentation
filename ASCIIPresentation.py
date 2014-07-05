import sublime
import sublime_plugin
import re
try:
    from lib.pyfiglet import figlet_format # ST2
except ImportError:
    from .lib.pyfiglet import figlet_format # ST3


REGEX = {
    "WHITE_SPACE_AND_TEXT" : re.compile(r"^(\s*)(.*)$"),
    "WHITE_SPACE"          : re.compile(r"\s+"),
    "NON_WHITE_SPACE"      : re.compile(r"\S+"),
    "NEW_LINE"             : re.compile(r"\n")
}

def indent_text(indentation, text):
    lines = map(lambda line: indentation + line, text.split("\n"))
    return "\n".join(lines)

def separate_indentation_from_text(text):
    match = re.search(REGEX["WHITE_SPACE_AND_TEXT"], text)
    return match.group(1), match.group(2)

def heading_text(font, text):
    indentation, text = separate_indentation_from_text(text)
    ascii_text = indent_text(indentation, figlet_format(text, font))
    return "##\n%s\n##\n" % ascii_text

def region_extended_back(region):
    return sublime.Region(region.begin() - 1, region.end())

def at_beginning_of_line(view, region):
    if region.begin() <= 0:
        return True
    return re.search(REGEX["NEW_LINE"], view.substr(region_extended_back(region)))

def text_extended_to_line_beginning(view, region):
    text = view.substr(region)
    no_line_break = not at_beginning_of_line(view, region)

    while no_line_break:
        region = region_extended_back(region)
        view.sel().subtract(region)
        view.sel().add(region)
        text = view.substr(region)
        no_line_break = not at_beginning_of_line(view, region)

    return text, region

def set_cursors_to_ends_of_selections(view):
    regions = list(view.sel())
    view.sel().clear()
    for region in regions:
        view.sel().add(sublime.Region(region.end(), region.end()))

def convert_title(view, edit, font_setting):
    for region in reversed(view.sel()):
        if region.empty():
            region = view.word(region)
            view.sel().add(region)

        text, region = text_extended_to_line_beginning(view, region)
        font = sublime.load_settings('ASCIIPresentation.sublime-settings').get(font_setting)
        view.replace(edit, region, heading_text(font, text))

    set_cursors_to_ends_of_selections(view)

def words_before_cursor(view, region):
    text, region = text_extended_to_line_beginning(view, region)
    return re.search(REGEX["NON_WHITE_SPACE"], text)

def white_space_before_cursor(view, region):
    return not at_beginning_of_line(view, region) and re.search(REGEX["WHITE_SPACE"], view.substr(region_extended_back(region)))


class ConvertTitleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        convert_title(self.view, edit, 'title_font')


class ConvertHeadingCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        convert_title(self.view, edit, 'heading_font')


class AddTerminalCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        terminal = self.terminal()

        for region in reversed(self.view.sel()):
            replacement = ""

            if region.empty():
                text = self.view.substr(region)
                if words_before_cursor(self.view, region):
                    # append
                    replacement = text + "\n" + terminal
                elif at_beginning_of_line(self.view, region):
                    # prepend
                    replacement = terminal + text
                else:
                    # prepend and indent
                    indentation, region = text_extended_to_line_beginning(self.view, region)
                    replacement = indent_text(indentation, terminal) + text
            else:
                if white_space_before_cursor(self.view, region):
                    # replace and indent
                    text, region = text_extended_to_line_beginning(self.view, region)
                    indentation, text = separate_indentation_from_text(text)
                    replacement = indent_text(indentation, terminal)
                else:
                    # replace
                    replacement = terminal

            self.view.replace(edit, region, replacement)

        set_cursors_to_ends_of_selections(self.view)

    def terminal(self):
        settings = sublime.load_settings('ASCIIPresentation.sublime-settings')
        width = settings.get('terminal_width')
        height = settings.get('terminal_height')

        hyphens = '-' * width
        spaces = ' ' * width
        title_bar_spaces = ' ' * (width - 3)
        lines = "|%s|\n" % spaces
        return " %s\n|ooo%s|\n|%s|\n%s %s\n" % (hyphens, title_bar_spaces, hyphens, lines * height, hyphens)


class NewSlideCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = sublime.load_settings('ASCIIPresentation.sublime-settings')
        number_of_lines = settings.get('lines_between_slides')
        lines = "\n" * number_of_lines

        for region in reversed(self.view.sel()):
            self.view.replace(edit, region, lines)

        set_cursors_to_ends_of_selections(self.view)
