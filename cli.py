#!/usr/bin/env python3
"""
Graph Artist - CLI tool for drawing custom designs on GitHub contribution graphs.
"""

import os
import sys
import json
import argparse
from font import text_to_matrix
from engine import (
    load_ascii_file,
    display_preview,
    get_start_date,
    build_schedule,
    run_fast_git_generation
)

BUILTIN_PATTERNS = {
    'heart': [
        '                                                    ',
        '          #####       #####                         ',
        '        #########   #########                       ',
        '        #####################                       ',
        '          #################                         ',
        '            #############                           ',
        '                #####                               ',
    ],
    'arcade': [
        '                                                    ',
        '              ##         ##                         ',
        '                ##     ##                           ',
        '              #############                         ',
        '             ###  #####  ###                        ',
        '            #################                       ',
        '            # #             #                       ',
    ],
    'wave': [
        '  ##                  ##                  ##        ',
        ' #  #                #  #                #  #       ',
        '     #              #    #              #    #      ',
        '      #            #      #            #      #     ',
        '       #          #        #          #        #    ',
        '        #        #          #        #          #   ',
        '         ########            ########            ## ',
    ]
}


def load_config():
    cfg_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(cfg_path):
        with open(cfg_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "author": {"name": "yalxss", "email": "111344379+yalxss@users.noreply.github.com", "timezone": "+0300"},
        "intensity_weights": {"0": 0, "1": 2, "2": 5, "3": 10, "4": 20},
        "default_year": 2026
    }


def main():
    config = load_config()
    parser = argparse.ArgumentParser(
        description="GitHub Contribution Graph Art & Canvas Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--text", type=str, help="Render text string onto contribution graph")
    mode_group.add_argument("--pattern", choices=list(BUILTIN_PATTERNS.keys()), default="heart", help="Use built-in art pattern")
    mode_group.add_argument("--file", type=str, help="Load 7x52 canvas from text file")

    parser.add_argument("--year", type=int, default=config.get("default_year", 2026), help="Target calendar year")
    parser.add_argument("--rolling", action="store_true", help="Use rolling 52 weeks from today")
    parser.add_argument("--preview", action="store_true", help="Preview only, do not generate commits")
    parser.add_argument("--generate", action="store_true", help="Generate commits directly into local repository")
    parser.add_argument("--repo-path", type=str, default=".", help="Local repository path")
    parser.add_argument("--author-name", type=str, default=config["author"]["name"], help="Git author name")
    parser.add_argument("--author-email", type=str, default=config["author"]["email"], help="Git author email")
    parser.add_argument("--tz", type=str, default=config["author"]["timezone"], help="Timezone offset (e.g. +0300)")

    args = parser.parse_args()

    # Determine matrix
    if args.text:
        matrix = text_to_matrix(args.text)
        title = f'Text: "{args.text}"'
    elif args.file:
        matrix = load_ascii_file(args.file)
        title = f'File: {os.path.basename(args.file)}'
    else:
        lines = BUILTIN_PATTERNS[args.pattern]
        from engine import parse_char_level
        matrix = [[parse_char_level(lines[r][c]) if c < len(lines[r]) else 0 for c in range(52)] for r in range(7)]
        title = f'Pattern: {args.pattern}'

    start_date = get_start_date(args.year, args.rolling)
    display_preview(matrix, f"{title} ({start_date})")

    if args.preview or not args.generate:
        if not args.preview:
            print("Use --generate to create commits directly, or --preview to inspect the canvas.")
        return

    weights = {int(k): int(v) for k, v in config["intensity_weights"].items()}
    schedule = build_schedule(matrix, start_date, weights)
    total = sum(schedule.values())

    print(f"Generating {total} commits across {len(schedule)} active days...")
    head_sha = run_fast_git_generation(schedule, args.repo_path, args.author_name, args.author_email, args.tz)
    print(f"Finished! Head commit: {head_sha[:8]}")


if __name__ == '__main__':
    main()
