A CommonMark-py (https://github.com/rtfd/CommonMark-py) renderer that outputs pretty plain text, i.e. not the original Markdown but something nicer for end users to see.

Example::

    import CommonMark
    import CommonMarkPlainText

    markdown_string = """# Hello!\n\nThis is [a link](https://github.com/JoshData/commonmark-py-plaintext)."""

    ast = CommonMark.Parser().parse(markdown_string)
    text = CommonMarkPlainText.CommonMarkPlainTextRenderer().render(ast)

    print(text)

Which outputs::

	Hello!
	######

	This is a link <https://github.com/JoshData/commonmark-py-plaintext>.

Why?

* Links appear more friendly than in the []() notation.
* Indentation is normalized.
* There are many ways to specify a heading in CommonMark, so heading styles are normalized in the output.
* Entity references like "&#1234;" are turned into Unicode characters.

Limitations:

* The html_inline and html_block nodes are not supported and will raise a ValueError exception.
* Images are rendered as "[image]" plus their alt text.

Testing:

There is no reference output for what this renderer should produce. But I've saved the output of all of the CommonMark tests into reference_output.txt. To check for consistency with this output, run::

    python3 test.py > reference_output.txt
    git diff

To see what's changed/broken.
