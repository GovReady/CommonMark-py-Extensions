# see https://github.com/rtfd/CommonMark-py/blob/master/CommonMark/render/html.py
# for the HTML renderer -- this is just a riff on that.

import re

import CommonMark.render.renderer


class RawHtmlNotAllowed(ValueError):
    def __init__(self):
        super(RawHtmlNotAllowed, self).__init__("Raw HTML cannot be rendered by the plain text renderer.")


class ListBlock:
    def __init__(self, list_type, start_value, bullet_char):
        self.list_type = list_type
        self.value = start_value
        self.bullet_char = bullet_char
    def __str__(self):
        # Does not cause indentation.
        return ""


class ItemBullet:
    def __init__(self, listblock):
        self.listblock = listblock
        self.emitted = None
    def __str__(self):
        # A bullet is emitted exactly once.
        if not self.emitted:
            if self.listblock.list_type == "bullet":
                self.emitted = self.listblock.bullet_char + " "
            elif self.listblock.list_type == "ordered":
                self.emitted = str(self.listblock.value) + ". "
                self.listblock.value += 1
            else:
                raise ValueError(self.listblock.list_type)
            return self.emitted

        # After that, it is just emitted as indentation.
        else:
            return " " * len(self.emitted)


class CommonMarkPlainTextRenderer(CommonMark.render.renderer.Renderer):
    def __init__(self):
        self.setext_heading_chars = ["#", "=", "-"]
        self.block_indent = []

    def render_indent(self, next_bullet=False):
        self.lit("".join(str(b) for b in self.block_indent))

    def text(self, node, entering=None):
        self.out(node.literal)
    def softbreak(self, node=None, entering=None):
        self.lit("\n")
        self.render_indent()
    def linebreak(self, node=None, entering=None):
        self.lit("\n")
        self.render_indent()
    def link(self, node, entering):
        if entering:
            self.link_start = len(self.buf)
        else:
            text = self.buf[self.link_start:]
            if text != node.destination:
                self.lit(" <" + node.destination + ">")
    def image(self, node, entering):
        if entering:
            self.lit('[image]')
        else:
            pass
    def emph(self, node, entering):
        self.lit("*") # same symbol entering & existing
    def strong(self, node, entering):
        self.lit("**") # same symbol entering & existing
    def paragraph(self, node, entering):
        if entering:
            self.render_indent()
        else:
            # adapted from the HtmlRenderer
            grandparent = node.parent.parent
            if grandparent is not None and grandparent.t == 'list' and  grandparent.list_data['tight']:
                self.lit("\n")
            else:
                self.lit("\n\n")
    def heading(self, node, entering):
        if entering:
            self.render_indent()
            self.heading_start = len(self.buf)
        else:
            if node.level <= len(self.setext_heading_chars):
                heading_len = len(self.buf) - self.heading_start
                if heading_len == 0:
                    # CommonMark requires that the heading still be emitted even if
                    # empty, so fall back to a setext-style heading.
                    self.lit("#" * node.level + " ")
                else:
                    self.lit("\n")
                    self.render_indent()
                    self.lit(self.setext_heading_chars[node.level-1] * heading_len)
            self.lit("\n")
            self.render_indent()
            self.lit("\n")
    def code(self, node, entering):
        # Just do actual CommonMark here. The backtick string around the literal
        # must have one more backtick than the number of consecutive backticks
        # in the literal.
        backtick_string = "`"
        while backtick_string in node.literal:
            backtick_string += "`"
        self.lit(backtick_string)
        if node.literal.startswith("`"):
            self.lit(" ")
        self.lit(node.literal) # this is correct as lit() and not out() for CommonMark-compliant output
        if node.literal.endswith("`"):
            self.lit(" ")
        self.lit(backtick_string)
    def code_block(self, node, entering):
        # open code block
        self.render_indent()
        self.emit_code_block_fence(node.literal, node.info)
        # each line, with indentation
        lines = node.literal.split("\n")
        while len(lines) > 0 and lines[-1] == "": lines.pop(-1)
        for line in lines:
            self.render_indent()
            self.lit(line + "\n") # this is correct as lit() and not out() for CommonMark-compliant output
        # close code block
        self.render_indent()
        self.emit_code_block_fence(node.literal)
        self.lit("\n")
    def emit_code_block_fence(self, literal, language=None):
        width = max([len(line.replace("\t", "    ")) for line in literal.split("\n")])
        self.lit("-" * width + "\n")
    def thematic_break(self, node, entering):
        self.render_indent()
        self.lit("-" * 60)
        self.lit("\n\n")
    def block_quote(self, node, entering):
        if entering:
            self.block_indent.append("> ")
            self.block_quote_start = len(self.buf)
        else:
            if self.block_quote_start == len(self.buf):
                # If no content, still must emit something.
                self.render_indent()
                self.out("\n\n")
            self.block_indent.pop(-1)
    def list(self, node, entering):
        if entering:
            # We could re-use the bullet character from the input:
            # bullet_char = node.list_data['bullet_char']
            # but for better normalization we'll choose a bullet char by
            # alternating through *, -, and + as we go deeper into levels.
            bullet_level = len(list(filter(lambda b : isinstance(b, ListBlock) and b.list_type == "bullet", self.block_indent)))
            bullet_char = ["*", "-", "+"][bullet_level % 3]
            # TODO #1: Two lists next to each other are distinguished as
            # different if they have either a different bullet (for bulleted
            # lists) or a different delimiter (the "." or ")" after the number,
            # for ordered lists). That distinction might be lost here and
            # would result in two lists being combined into one.
            # TODO #2: A list can be loose or tight, but we don't output them
            # any differently.
            self.block_indent.append(ListBlock(node.list_data['type'], node.list_data['start'], bullet_char))
        else:
            self.block_indent.pop(-1)
    def item(self, node, entering):
        if entering:
            # Find the ListBlock that was most recently added to self.block_indent.
            parent_list = [b for b in self.block_indent if isinstance(b, ListBlock)][-1]
            self.block_indent.append(ItemBullet(parent_list))
            self.item_start = len(self.buf)
        else:
            if len(self.buf) == self.item_start:
                # Always emit a bullet even if there was no content.
                self.render_indent()
                self.lit("\n\n")
            self.block_indent.pop(-1)

    def html_inline(self, node, entering):
        raise RawHtmlNotAllowed()

    def html_block(self, node, entering):
        raise RawHtmlNotAllowed()

    def custom_inline(self, node, entering):
        # copied from the HTML renderer
        if entering and node.on_enter:
            self.lit(node.on_enter)
        elif (not entering) and node.on_exit:
            self.lit(node.on_exit)

    def custom_block(self, node, entering):
        # copied from the HTML renderer
        self.cr()
        if entering and node.on_enter:
            self.lit(node.on_enter)
        elif (not entering) and node.on_exit:
            self.lit(node.on_exit)
        self.cr()

class CommonMarkToCommonMarkRenderer(CommonMarkPlainTextRenderer):
    def __init__(self):
        super(CommonMarkToCommonMarkRenderer, self).__init__()
        self.setext_heading_chars = ["=", "-"]

    def out(self, s):
        # Escape punctuation.
        # http://spec.commonmark.org/0.25/#ascii-punctuation-character
        escape_chars = ["!", "\"", "#", "$", "%", "&", "'", "(", ")", "*", "+", ",", "-", ".", "/", ":", ";", "<", "=", ">", "?", "@", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~"]
        s = "".join(("\\" if c in escape_chars else "") + c for c in s)
        super(CommonMarkToCommonMarkRenderer, self).out(s)

    def linebreak(self, node=None, entering=None):
        self.lit("\\\n")
        self.render_indent()

    def link(self, node, entering):
        # Determine if the link label and the destination are the same by rendering
        # this node using the plain text renderer. Luckily, if they are the same,
        # the plain text renderer simply emits the label without the destination.
        link_label = CommonMarkPlainTextRenderer().render(node)
        if (link_label == node.destination) or ("mailto:" + link_label.lower().lower() == node.destination.lower()) \
            and re.match(r"[A-Za-z][A-Za-z0-9+\.-]{1,32}:[^<> ]*$", node.destination):
            # Emit an autolink.
            if entering:
                destination = node.destination
                if destination.lower().startswith("mailto:"):
                    destination = destination[7:]
                self.lit("<")
                self.lit(node.destination)
                self.lit(">")
                self.autolink_start = len(self.buf)
            else:
                # kill any content emitted within this node
                self.buf = self.buf[0:self.autolink_start]
        else:
            if entering:
                self.lit("[")
            else:
                self.lit("](")
                # When wrapping the destination with parens, then internal parens must be
                # either well-nested (which is hard to detect) or escaped.
                self.lit(node.destination.replace("(", "\\(").replace(")", "\\)"))
                if node.title:
                    self.lit(" \"")
                    # When wrapping the title in double quotes, internal double quotes
                    # must be escaped.
                    self.lit(node.title.replace("\"", "\\\""))
                    self.lit("\"")
                self.lit(")")

    def image(self, node, entering):
        if entering:
            self.lit("![")
        else:
            self.lit("](")
            # same as link, see above
            self.lit(node.destination.replace("(", "\\(").replace(")", "\\)"))
            if node.title:
                # same as link, see above
                self.lit(" \"")
                self.lit(node.title.replace("\"", "\\\""))
                self.lit("\"")
            self.lit(")")

    def heading(self, node, entering):
        if node.level <= 2:
            # Prefer setext-style heading for levels 1 and 2, because it is
            # the only style that supports multi-line content within it, which
            # we might have (and we don't know at this point).
            super(CommonMarkToCommonMarkRenderer, self).heading(node, entering)
        else:
            # Use ATX-style headings for other levels.
            if entering:
                self.lit("#" * node.level + " ")
                self.block_indent.append(" " * (node.level+1))
            else:
                self.lit("\n")
                self.block_indent.pop(-1)

    def emit_code_block_fence(self, content, info_string=None):
        # Choose a fence string that does not appear in the content
        # of the code block. A fence string can made made up of
        # backticks or tildes, but we'll stick to backticks.
        fence_string = "```"
        while fence_string in content:
            fence_string += fence_string[0]
        self.lit(fence_string)
        if info_string:
            self.out(info_string)
        self.lit("\n")

    def html_inline(self, node, entering):
        self.lit(node.literal)

    def html_block(self, node, entering):
        self.lit('\n')
        self.lit(node.literal)
        self.lit('\n')

if __name__ == "__main__":
    # Example!
    #
    # Convert the Markdown on standard input to plain text on standard output.

    import sys
    import CommonMark

    ast = CommonMark.Parser().parse(sys.stdin.read())
    sys.stdout.write(CommonMarkPlainTextRenderer().render(ast))
