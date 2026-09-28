#!/usr/bin/env python3
"""Add one paper to the year-grouped publications in about-zh.md.

Edit PAPER_TEMPLATE below, then run:
  python3 tools/add_paper.py --from-template --dry-run
  python3 tools/add_paper.py --from-template

The original one-line form still works:
  python3 tools/add_paper.py 2027 corresponding 'A. Researcher and Xinze Zhang. Paper title. *Journal Name*, 2027. Accepted.'

The citation is Markdown. Write your name as plain text once; this tool adds
its existing red/gray styling and, for a corresponding author, the 📩 symbol.
"""

import argparse
import re
from datetime import date
from pathlib import Path

# Edit this block to add one paper with --from-template. Leave authors/title/
# journal blank until you have real paper details. Both of these publication
# details work with the same template:
#   accepted:  "Accepted for publication"
#   published: "Volume 76, Part C, Pages 105047"
# The final parenthesized note is assembled from "notes" automatically.
PAPER_TEMPLATE = {
    'year': date.today().year,
    'role': 'coauthor',  # first | corresponding | coauthor
    'name': 'Xinze Zhang',
    'authors': '',       # e.g. 'Mingyu Xu, Shiming Deng, Shenghao Qiao, and Xinze Zhang'
    'title': '',         # e.g. 'ViDSum-TSF: Long-Document-Driven ...'
    'journal': '',       # e.g. 'Journal of Systems Architecture'
    'publication_details': '',  # accepted or volume/part/pages/article number
    'notes': '',         # e.g. '唯一通讯, JCR Q1, IF 5.3'
}


SECTION_START = '<div class="publication-years">'
SECTION_END = '\n## Arxiv'
ROW_START = '<div class="grid grid--px-2" style="border-bottom:'
PAPER_CELL = '<div class="cell cell--12 cell--md-auto" markdown="1">\n\n'
YEAR_RE = re.compile(r'(?m)^    (\d{4})$')




def build_citation(paper: dict) -> str:
    """Build the citation text used by both accepted and published papers."""
    required = ('authors', 'title', 'journal', 'publication_details', 'notes')
    missing = [key for key in required if not isinstance(paper.get(key), str) or not paper[key].strip()]
    if missing:
        raise ValueError('Fill these PAPER_TEMPLATE fields: ' + ', '.join(missing))
    authors = paper['authors'].strip().rstrip('.')
    title = paper['title'].strip().rstrip('.')
    journal = paper['journal'].strip().strip('*').strip().rstrip(',.')
    details = paper['publication_details'].strip().rstrip('.')
    notes = paper['notes'].strip().strip('()').strip()
    return f'{authors}. {title}. *{journal}*, {paper["year"]}. {details}. ({notes})'


def add_paper(source: str, year: int, role: str, citation: str, name: str) -> str:
    if source.count(SECTION_START) != 1:
        raise ValueError('Expected exactly one year-grouped publications section')
    section_start = source.index(SECTION_START) + len(SECTION_START)
    section_end = source.find(SECTION_END, section_start)
    if section_end < 0:
        raise ValueError('Could not find the end of the publications section')
    section = source[section_start:section_end]

    citation = citation.strip()
    if not citation or '\n' in citation or citation.startswith('- '):
        raise ValueError('Supply one Markdown citation on one line, without a bullet')
    if not name or citation.count(name) != 1:
        raise ValueError(f'The citation must contain {name!r} exactly once')
    if '<font' in citation or '<strong' in citation:
        raise ValueError('Supply the author name as plain text; styling is automatic')
    color = '#DC3522' if role in ('first', 'corresponding') else '#5D5D5D'
    styled_name = f'<strong><font color="{color}">{name}</font></strong>'
    if role == 'corresponding' and not citation.split(name, 1)[1].startswith('📩'):
        styled_name += '📩'
    paper = '- ' + citation.replace(name, styled_name, 1)
    if paper in section:
        raise ValueError('This citation is already in the publications section')

    year_matches = list(YEAR_RE.finditer(section))
    years = [int(match.group(1)) for match in year_matches]
    row_starts = [match.start() for match in re.finditer(r'(?m)^' + re.escape(ROW_START), section)]
    if not years or len(years) != len(row_starts) or years != sorted(set(years), reverse=True):
        raise ValueError('Publication year rows are missing, duplicated, or unsorted')

    if year in years:
        index = years.index(year)
        row_end = row_starts[index + 1] if index + 1 < len(years) else len(section)
        cell_start = section.find(PAPER_CELL, year_matches[index].end(), row_end)
        if cell_start < 0:
            raise ValueError(f'Could not find the paper list for {year}')
        insert_at = cell_start + len(PAPER_CELL)
        section = section[:insert_at] + paper + '\n' + section[insert_at:]
    else:
        row = (
            f'<div class="grid grid--px-2" style="border-bottom: 1px solid #e6e6e6; margin-bottom: 1rem;">\n'
            f'<div class="cell cell--12 cell--md-shrink" style="font-weight: 700; color: #DC3522;">\n'
            f'    {year}\n'
            f'</div>\n'
            f'<div class="cell cell--12 cell--md-auto" markdown="1">\n\n'
            f'{paper}\n\n'
            f'</div>\n'
            f'</div>\n\n'
        )
        older = next((i for i, existing in enumerate(years) if existing < year), None)
        insert_at = row_starts[older] if older is not None else section.rfind('\n</div>')
        if insert_at < 0:
            raise ValueError('Could not find an insertion point for the new year')
        section = section[:insert_at] + row + section[insert_at:]

    return source[:section_start] + section + source[section_end:]


class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=HelpFormatter)
    parser.add_argument('year', type=int, nargs='?', default=date.today().year,
                        help='Publication or acceptance year')
    parser.add_argument('role', choices=('first', 'corresponding', 'coauthor'),
                        nargs='?', default='coauthor',
                        help='Your role; first and corresponding get a red author name and bullet')
    parser.add_argument('citation', nargs='?', default=None,
                        help='One complete Markdown citation; prompts if omitted')
    parser.add_argument('--name', default='Xinze Zhang', help='Your name as it appears in this citation')
    parser.add_argument('--file', type=Path, default=Path(__file__).resolve().parents[1] / 'about-zh.md',
                        help='Target Markdown file')
    parser.add_argument('--dry-run', action='store_true', default=False,
                        help='Print the new citation without editing the file')
    parser.add_argument('--from-template', action='store_true', default=False,
                        help='Use the editable PAPER_TEMPLATE near the top of this file')
    args = parser.parse_args()
    if args.from_template:
        if args.citation is not None:
            parser.error('Use either --from-template or a citation argument')
        try:
            args.citation = build_citation(PAPER_TEMPLATE)
        except ValueError as error:
            parser.error(str(error))
        args.year = PAPER_TEMPLATE['year']
        args.role = PAPER_TEMPLATE['role']
        args.name = PAPER_TEMPLATE['name']
    elif args.citation is None:
        try:
            args.citation = input('Citation (one line, plain author name): ')
        except EOFError:
            parser.error('Citation required; pass it as an argument or enter it at the prompt')
    if not 1900 <= args.year <= 2100:
        parser.error('Year must be between 1900 and 2100')
    try:
        before = args.file.read_text(encoding='utf-8')
        after = add_paper(before, args.year, args.role, args.citation, args.name)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.dry_run:
        print('Would add:\n' + next(line for line in after.splitlines() if
                                    line.startswith('- ') and line not in before.splitlines()))
    else:
        args.file.write_text(after, encoding='utf-8')
        print(f'Added paper under {args.year} in {args.file}')


if __name__ == '__main__':
    main()
