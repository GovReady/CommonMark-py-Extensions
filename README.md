Tables for CommonMark-py
========================

This package provides classes for extending [CommonMark-py](https://github.com/rtfd/CommonMark-py), a CommonMark rendering library for Python, with
parsing and rendering tables in [GitHub Flavored Markdown](https://github.github.com/gfm/#tables-extension-)
format, as well as our own format for multi-line table cells that support
embedded block markup.

This library is tightly linked to the CommonMark-py internals and has been tested only with `CommonMark==0.7.4`.

Usage is similar to the upstream library:

```python
>>> import CommonMarkTables
>>> CommonMarkTables.commonmark("""
... | Header 1 | Header 2 |
... | -------- | -------- |
... | Cells    | **can**  |
... | `have`   | inlines. |
... """)
'<table>\n<thead>\n<tr>\n<th>Header 1</th>\n<th>Header 2</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>Cells</td>\n<td><strong>can</strong></td>\n</tr>\n<tr>\n<td><code>have</code></td>\n<td>inlines.</td>\n</tr>\n</tbody>\n</table>\n'
```

You can also instantiate (and subclass, if you like) the parser and renderer separately:

```python
markup = """
| Sample | Header |
| -----: | :----: |
| A      | **bold** |
| C      | D      |
"""

from CommonMarkTables import ParserWithTables, RendererWithTables
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

Note how the alignment is set with `:` as per GitHub Flavored Markdown tables.

To use multi-line cells that can hold embedded block formatting (e.g. paragraphs
and lists within cells), use `=`s instead of hyphens below the header and separate all rows with rows of `=`s (optionally ending with another row of `=`s):

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