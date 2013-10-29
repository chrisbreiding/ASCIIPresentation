import sublime
import sublime_plugin
import re
from pyfiglet import Figlet


REGEX = {
    "WHITE_SPACE_AND_TEXT" : re.compile(r"^(\s*)(.*)$"),
    "WHITE_SPACE"          : re.compile(r"\s+"),
    "NON_WHITE_SPACE"      : re.compile(r"\S+"),
    "NEW_LINE"             : re.compile(r"\n"),
    "MD_FILE"              : re.compile(r"\.(?:md|markdown)$")
}

def indent_text(indentation, text):
    lines = map(lambda line: indentation + line, text.split("\n"))
    return "\n".join(lines)

def separate_indentation_from_text(text):
    match = re.search(REGEX["WHITE_SPACE_AND_TEXT"], text)
    return match.group(1), match.group(2)

def heading_text(font, text):
    indentation, text = separate_indentation_from_text(text)
    ascii_text = indent_text(indentation, Figlet(font=font).renderText(text))
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


class AsciiPresentationConvertMarkdownCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.blocks = self.md_blocks()
        self.inlines = self.md_inlines()

        if self.window.active_view():
            view = self.window.active_view()
            file_name = view.file_name()
            if self.is_markdown_file(file_name):
                text = view.substr(sublime.Region(0, view.size()))
                md = self.parse(text)
                text = self.render(md)

                file_name = re.sub(REGEX['MD_FILE'], '.pres', file_name)
                file = open(file_name, 'w+')
                file.write(text)
                file.close()
                self.window.open_file(file_name)

            else:
                sublime.status_message('Can only convert markdown files (.md or .markdown) into ASCII presentation')

    def is_markdown_file(self, file_name):
        return re.search(REGEX['MD_FILE'], file_name)

    def parse(self, md):
        parsed_md = []

        for paragraph in md.split("\n\n"):
            parsed = self.parse_blocks(paragraph)
            if parsed:
                parsed_md.append(parsed)

        return parsed_md

    def render(self, ast):
        rendered_text = ''
        for tree in ast:
            rendered_text += tree['type'] + ":\n"
            rendered_text += ''.join(tree['components']) + "\n\n"

        return rendered_text

    def parse_blocks(self, text):
        if self.is_only_whitespace(text):
            return False

        for block in self.blocks:
            if re.search(block['regex'], text):
                return {
                    'type': block['type'],
                    'components': block['parse'](text)
                }

        return {
            'type': 'p',
            'components': self.parse_components(text)
        }

    def parse_components(self, text):
        # components = []

        # for inline in self.inlines:
        #     if re.search(inline['regex'], text):
        #         components.append({
        #             'type': inline['type'],
        #             'content': inline['parse'](text)
        #         })
        return text

    def parse_heading(self, heading):
        return re.sub(re.compile(r"^#+\s+"), '', heading)

    def render_h1(self, text):
        font = sublime.load_settings('ASCIIPresentation.sublime-settings').get('title_font')
        return heading_text(font, text)

    def render_h2(self, text):
        font = sublime.load_settings('ASCIIPresentation.sublime-settings').get('heading_font')
        return heading_text(font, text)

    def render_h3(self, text):
        return text + ' ###'

    def noop_with_return(self, arg):
        return arg

    def is_only_whitespace(self, text):
        return not re.search(REGEX["NON_WHITE_SPACE"], text)

    def md_blocks(self):
        return [
            {
                'type': 'h1',
                'regex': re.compile(r"^#\s+.+"),
                'parse': self.parse_heading,
                'render': self.render_h1
            },
            {
                'type': 'h2',
                'regex': re.compile(r"^#{2}\s+.+"),
                'parse': self.parse_heading,
                'render': self.render_h2
            },
            {
                'type': 'h3',
                'regex': re.compile(r"^#{3,6}\s+.+"),
                'parse': self.parse_heading,
                'render': self.render_h3
            },
            {
                'type': 'uli',
                'regex': re.compile(r"^\s*[+*-]\s+.+"),
                'parse': self.noop_with_return,
                'render': self.noop_with_return
            },
            {
                'type': 'oli',
                'regex': re.compile(r"^\s*\d+\.\s+.+"),
                'parse': self.noop_with_return,
                'render': self.noop_with_return
            },
            {
                'type': 'code',
                'regex': re.compile(r"^\s*```"),
                'parse': self.noop_with_return,
                'render': self.noop_with_return
            },
            {
                'type': 'blockquote',
                'regex': re.compile(r"^\s*\>"),
                'parse': self.noop_with_return,
                'render': self.noop_with_return
            }
        ]

    def md_inlines(self):
        return [
            {
                'type': 'img',
                'regex': re.compile(r"\!\[.*\]\(.+\)"),
                'parse': self.noop_with_return,
                'render': self.noop_with_return
            },
            {
                'type': 'link',
                'regex': re.compile(r"\[.+\]\(.+\)"),
                'parse': self.noop_with_return,
                'render': self.noop_with_return
            },
            {
                'type': 'em',
                'regex': re.compile(r"(?P<symbol>[*_])\w+(?P=symbol)"),
                'parse': self.noop_with_return,
                'render': self.noop_with_return
            },
            {
                'type': 'strong',
                'regex': re.compile(r"(?P<symbol>[*_])(?P=symbol)\w+(?P=symbol)(?P=symbol)"),
                'parse': self.noop_with_return,
                'render': self.noop_with_return
            }
        ]

