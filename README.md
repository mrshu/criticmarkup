# criticmarkup

Fast CriticMarkup preprocessor with multiple output formats (AsciiDoc, Markdown, LaTeX).

## Install

With `uv`:

```bash
uv tool install criticmarkup
```

With `pip`:

```bash
python -m pip install criticmarkup
```

## Dev install (uv)

```bash
uv sync --extra dev
```

## Usage

Convert a file (format inferred from extension):

```bash
criticmarkup convert input.md --in-place
```

Read from stdin, write to stdout:

```bash
cat input.md | criticmarkup convert --format markdown
```

Override a preset template:

```bash
criticmarkup convert input.md --addition-replacement-template "<ins>{CURRENT}</ins>"
```

List built-in presets:

```bash
criticmarkup presets
```

## CriticMarkup syntax

This tool follows the core CriticMarkup syntax (as described in the CriticMarkup Toolkit):

- Addition: `{++added++}`
- Deletion: `{--deleted--}`
- Substitution: `{~~old~>new~~}`
- Comment: `{>>comment<<}`
- Highlight: `{==highlight==}` (commonly followed by a comment: `{==highlight==}{>>comment<<}`)

## Change list placeholder

If the input contains `{+-~TOC-CHANGES~-+}`, it will be replaced with a generated list of change IDs/notes.

## Configuration

You can override templates either via CLI flags (e.g. `--addition-replacement-template`) or a TOML config file:

```toml
[templates]
addition_replacement_template = "<ins>{CURRENT}</ins>"
deletion_replacement_template = "<del>{PREVIOUS}</del>"
```

Common template variables:

- `{CURRENT}`, `{PREVIOUS}`: raw matched text
- `{CURRENT_SINGLELINE}`, `{PREVIOUS_SINGLELINE}`: whitespace collapsed
- `{CURRENT_SHORT}`, `{PREVIOUS_SHORT}`: shortened (controlled by `--shorten-notes-at`)
- `{CHANGE_ID}`, `{NOTE}`: generated id and note (for change refs / change list items)

## Caveats

CriticMarkup is designed to be readable and regex-friendly, but you can still break output if you try hard enough.
In particular:

- Avoid newlines inside CriticMarkup tags when possible.
- When mixing with Markdown formatting, wrap the entire Markdown span in a single CriticMarkup mark (don’t split `*...*`).

## Examples

### Markdown

Input (`doc.md`):

```md
Intro paragraph.

{+-~TOC-CHANGES~-+}

We {++add new text++} here.
We {--remove old text--} here.
We {~~replace this~>with that~~} here.
We can {==highlight==} something.
And leave a {>>reviewer note<<} comment.
```

Command:

```bash
criticmarkup convert doc.md --in-place
```

Output (`doc.md`):

```md
Intro paragraph.

- [addition-1](#addition-1): Added "add new text"
- [deletion-1](#deletion-1): Deleted "remove old text"
- [substitution-1](#substitution-1): Changed "replace this" to "with that"

We <a id="addition-1"></a><!-- Added "add new text" -->
<ins>add new text</ins> here.
We <a id="deletion-1"></a><!-- Deleted "remove old text" -->
<del>remove old text</del> here.
We <a id="substitution-1"></a><!-- Changed "replace this" to "with that" -->
<del>replace this</del><ins>with that</ins> here.
We can <mark>highlight</mark> something.
And leave a <!-- reviewer note --> comment.
```

### AsciiDoc

Input (`doc.adoc`):

```adoc
Intro paragraph.

{+-~TOC-CHANGES~-+}

We {++add new text++} here.
We {--remove old text--} here.
We {~~replace this~>with that~~} here.
We can {==highlight==} something.
And leave a {>>reviewer note<<} comment.
```

Command:

```bash
criticmarkup convert doc.adoc --in-place
```

Output (`doc.adoc`):

```adoc
Intro paragraph.

- <<addition-1>>
- <<deletion-1>>
- <<substitution-1>>

We [[addition-1, Added "add new text"]]
[red]#*add new text*# here.
We [[deletion-1, Deleted "remove old text"]]
footnote:[In previous version this said "remove old text"] here.
We [[substitution-1, Changed "replace this" to "with that"]]
[red]#*with that*#
footnote:[In previous version this said "replace this"] here.
We can [yellow]#highlight# something.
And leave a footnote:[reviewer note] comment.
```

### LaTeX

Input (`doc.tex`):

```tex
Intro paragraph.

{+-~TOC-CHANGES~-+}

We {++add new text++} here.
We {--remove old text--} here.
We {~~replace this~>with that~~} here.
We can {==highlight==} something.
And leave a {>>reviewer note<<} comment.
```

Command:

```bash
criticmarkup convert doc.tex --in-place
```

Output (`doc.tex`):

```tex
Intro paragraph.

\item addition-1: Added "add new text"
\item deletion-1: Deleted "remove old text"
\item substitution-1: Changed "replace this" to "with that"

We % addition-1: Added "add new text"
\underline{{add new text}} here.
We % deletion-1: Deleted "remove old text"
\sout{{remove old text}} here.
We % substitution-1: Changed "replace this" to "with that"
\sout{{replace this}}\underline{{with that}} here.
We can \fbox{{highlight}} something.
And leave a % NOTE: reviewer note comment.
```
