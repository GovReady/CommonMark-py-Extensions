# see https://github.com/rtfd/CommonMark-py/blob/master/CommonMark/render/html.py
# for the HTML renderer -- this is just a riff on that.

import CommonMark.render.renderer


class RawHtmlNotAllowed(ValueError):
    def __init__(self):
        super(RawHtmlNotAllowed, self).__init__("Raw HTML cannot be rendered by the plain text renderer.")


class ListBlock:
    def __init__(self, list_type, start_value):
        self.list_type = list_type
        self.value = start_value
    def __str__(self):
        # Does not cause indentation.
        return ""


class ItemBullet:
    def __init__(self, listblock):
        self.listblock = listblock
        self.emitted = False
    def __str__(self):
        # A bullet is emitted exactly once.
        if not self.emitted:
            self.emitted = True
            return "* "

        # After that, it is just emitted as indentation.
        else:
            return "  "


class CommonMarkPlainTextRenderer(CommonMark.render.renderer.Renderer):
    def __init__(self):
        self.block_indent = []

    def render_indent(self, next_bullet=False):
        self.lit("".join(str(b) for b in self.block_indent))

    def text(self, node, entering=None):
        self.out(node.literal)
    def softbreak(self, node=None, entering=None):
        self.out("\n")
        self.render_indent()
    def linebreak(self, node=None, entering=None):
        self.out("\n")
        self.render_indent()
    def link(self, node, entering):
        if entering:
            self.link_start = len(self.buf)
        else:
            text = self.buf[self.link_start:]
            if text != node.destination:
                self.out(" <" + node.destination + ">")
    def image(self, node, entering):
        if entering:
            self.out('[image]')
        else:
            pass
    def emph(self, node, entering):
        self.out("*") # same symbol entering & existing
    def strong(self, node, entering):
        self.out("**") # same symbol entering & existing
    def paragraph(self, node, entering):
        if entering:
            self.render_indent()
        else:
            self.out("\n\n")
    def heading(self, node, entering):
        if entering:
            self.render_indent()
            self.heading_start = len(self.buf)
        else:
            heading_chars = ["#", "=", "-"]
            if node.level <= len(heading_chars):
                heading_len = len(self.buf) - self.heading_start
                self.out("\n")
                self.render_indent()
                self.out(heading_chars[node.level-1] * heading_len)
            self.out("\n")
            self.render_indent()
            self.out("\n")
    def code(self, node, entering):
        self.out("```") # better way to render this?
        self.out(node.literal)
        self.out("```")
    def code_block(self, node, entering):
        max_line_len = max([len(line.replace("\t", "    ")) for line in node.literal.split("\n")])
        # open code block
        self.render_indent()
        self.out("-" * max_line_len + "\n")
        # each line, with indentation
        lines = node.literal.split("\n")
        while len(lines) > 0 and lines[-1] == "": lines.pop(-1)
        for line in lines:
            self.render_indent()
            self.out(line + "\n")
        # close code block
        self.render_indent()
        self.out("-" * max_line_len + "\n\n")
    def thematic_break(self, node, entering):
        self.render_indent()
        self.out("-" * 60)
        self.out("\n\n")
    def block_quote(self, node, entering):
        if entering:
            self.block_indent.append("> ")
        else:
            self.block_indent.pop(-1)
    def list(self, node, entering):
        if entering:
            self.block_indent.append(ListBlock(node.list_data['type'], node.list_data['start']))
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
                self.out("\n\n")
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

if __name__ == "__main__":
    # Example!
    #
    # Convert the Markdown on standard input to plain text on standard output.

    import sys
    import CommonMark

    ast = CommonMark.Parser().parse(sys.stdin.read())
    sys.stdout.write(CommonMarkPlainTextRenderer().render(ast))
