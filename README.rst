A `CommonMark-py`_<https://github.com/rtfd/CommonMark-py> renderer that outputs pretty plain text (not the original Markdown but something nicer for end users to see) or round-trips to compliant CommonMark.

The library was built against `CommonMark 0.25`_<http://spec.commonmark.org/0.25/> and `CommonMark-py 0.6.4`_<https://github.com/rtfd/CommonMark-py>.

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

Or using the CommonMarkToCommonMarkRenderer instead of the CommonMarkPlainTextRenderer, you get::

	Hello\!
	=======

	This is [a link](https://github.com/JoshData/commonmark-py-plaintext)\.

Why have a special renderer for plain text?

* Links appear more friendly than in the []() notation.
* Indentation is normalized.
* There are many ways to specify a heading in CommonMark, so heading styles are normalized in the output.
* Entity references like "&#1234;" are turned into Unicode characters.

Limitations:

* The html_inline and html_block nodes are not supported and will raise a ValueError exception.
* Images are rendered as "[image]" plus their alt text.
* The CommonMarkToCommonMarkRenderer is pretty good but is not complete. It also has some additional limitations: lists next to each other may be combined, the loose/tight distinction of lists is not captured in output.

Testing:

There is no reference output for what this renderer should produce. But I've saved the output of all of the CommonMark tests into reference_output.txt. To check for consistency with this output, run::

    python3 test.py > reference_output.txt
    git diff

To see what's changed/broken.
