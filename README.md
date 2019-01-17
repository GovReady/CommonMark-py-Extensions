CommonMark-py-Extensions
========================

This package extends the [commonmark](https://github.com/rtfd/CommonMark-py) CommonMark rendering library for Python with:

* Tables in [GitHub Flavored Markdown](https://github.github.com/gfm/#tables-extension-), with a futher extension for multi-line table cells that support
embedded block markup.
* A new renderer to convert CommonMark to plain text that is prettier than the original CommonMark, and a renderer that turns CommonMark back into CommonMark again.

This library is tightly linked to the commonmark internals and has been tested only with `commonmark==0.8.0`.

NOTE: This project is a work-in-progress. It is closely compatible with GitHub Flavored Markdown but deviates a bit in edge cases and block-end rules.

Installation
------------

	pip install commonmarkextensions

Usage
-----

### Tables

Usage is similar to the upstream library. To render tables:

```python
>>> import commonmark_extensions.tables
>>> commonmark_extensions.tables.commonmark("""
... | Header 1 | Header 2 |
... | -------- | -------- |
... | Cells    | **can**  |
... | `have`   | inlines. |
... """)
'<table>\n<thead>\n<tr>\n<th>Header 1</th>\n<th>Header 2</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>Cells</td>\n<td><strong>can</strong></td>\n</tr>\n<tr>\n<td><code>have</code></td>\n<td>inlines.</td>\n</tr>\n</tbody>\n</table>\n'
```

Column text alignment is set with `:` as per GitHub Flavored Markdown tables. This example sets the first column to be right aligned and the second column to be center-aligned:

```markdown
| Sample | Header |
| -----: | :----: |
| A      | **bold** |
| C      | D      |
```

The tables extension also accepts our own multi-line cell format, in which cells can hold embedded block formatting (e.g. paragraphs
and lists within cells). Use `=` instead of `-` below the header and then separate all rows with rows of `=`s (optionally ending the table with another row of `=`s), as in:

```python
markup = """
| Sample | Header |
| ====== | ====== |
| * A    | * B    |
| * C    | * D    |
| ====== | ====== |
| > C    | D      |
| ====== | ====== |
"""
```

The resulting HTML is:

```html
<table>
<thead>
<tr>
<th>Sample</th>
<th>Header</th>
</tr>
</thead>
<tbody>
<tr>
<td><ul>
<li>A</li>
<li>C</li>
</ul>
</td>
<td><ul>
<li>B</li>
<li>D</li>
</ul>
</td>
</tr>
<tr>
<td><blockquote>
<p>C</p>
</blockquote>
</td>
<td>D</td>
</tr>
</tbody>
</table>
```

### Plain text

The library also includes new renderers for plain text and for outputting back to CommonMark. Most of the
input is left unchanged by these renderers. E.g. `*Italic*` in the input is rendered as `*Italic*` in the
output. But some CommonMark formatting --- especially links --- is confusing for non-technical end users.
The plain text renderer fixes up and normalizes markup:

* Links appear more friendly than in the []() notation.
* Indentation is normalized.
* There are many ways to specify a heading in CommonMark, so heading styles are normalized in the output.
* Entity references like "&#1234;" are turned into Unicode characters.

Use the plain text renderer as follows:

```python
>>> import commonmark_extensions.plaintext
>>> pt = commonmark_extensions.plaintext.commonmark("""
...   # Good morning!
... 
...   See [our website](https://www.govready.com) for details.
... """)
>>> print(pt)
```

which generates

```text
Good morning!
#############

See our website <https://www.govready.com> for details.
```

The CommonMark-to-CommonMark renderer can only be used by instantiating a parser and renderer --- see below.

Limitations:

* The html_inline and html_block nodes are not supported and will raise a RawHtmlNotAllowed exception.
* Images are rendered as "[image]" plus their alt text.

Advanced Usage
--------------

You can also instantiate (and subclass, if you like) the parser and renderers separately:

### Advanced Usage for Tables

```python
markup = """
| Sample | Header |
| -----: | :----: |
| A      | **bold** |
| C      | D      |
"""

from commonmark_extensions.tables import ParserWithTables, RendererWithTables
parser = ParserWithTables()
ast = parser.parse(markup)
print(RendererWithTables().render(ast))
```

This outputs:

```html
<table>
<thead>
<tr>
<th align="right">Sample</th>
<th align="center">Header</th>
</tr>
</thead>
<tbody>
<tr>
<td align="right">A</td>
<td align="center"><strong>bold</strong></td>
</tr>
<tr>
<td align="right">C</td>
<td align="center">D</td>
</tr>
</tbody>
</table>
```

### Advanced Usage for Plain Text

Plain text rendering using a parser and renderer:

```python
import commonmark
from commonmark_extensions.plaintext import PlainTextRenderer
parser = commonmark.Parser()
ast = parser.parse(markup)
print(PlainTextRenderer().render(ast))
```

There is a second renderer for generating CommonMark, i.e. normalizing the input CommonMark
into more CommonMark.

```python
>>> markup = """
... # Good morning!
... 
... See [our website](https://www.govready.com) for details.
... """
>>> import commonmark
>>> from commonmark_extensions.plaintext import CommonMarkToCommonMarkRenderer
>>> parser = commonmark.Parser()
>>> ast = parser.parse(markup)
>>> print(CommonMarkToCommonMarkRenderer().render(ast))
Good morning\!
==============

See [our website](https://www.govready.com) for details.
```

The CommonMarkToCommonMarkRenderer is pretty good but is not complete. It also has some additional limitations: it over-zealously backslash-escapes punctuation characters because it can't tell when it would be safe to not do so, lists next to each other may be combined, the loose/tight distinction of lists is not captured in output.

Tests
-----

There is no reference output for what the plain text renderer should produce. But I've saved the output of all of the CommonMark spec examples into `reference_output.txt` so that as this library evolves we can see changes. To check for consistency with previous output of this library, run::

    python3 commonmark_extensions/make_reference_output.py > reference_output.txt
    git diff

The PlainTextRenderer is tested by round-tripping CommonMark (parsing, then outputing it as CommonMark), and then parsing that and outputting to HTML. The final HTML should match the HTML that you'd get from just rendering to HTML in one step. 


For Project Maintainers
-----------------------

To publish a universal wheel to pypi::

        pip3 install twine
        rm -rf dist
        python3 setup.py bdist_wheel --universal
        twine upload dist/*
        git tag v1.0.XXX
        git push --tags
