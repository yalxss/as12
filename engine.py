"""
Core git commit generation and contribution calendar matrix engine.
"""

import os
import subprocess
import datetime
from typing import Dict, List

# GitHub Dark Theme Palette (Truecolor RGB)
COLOR_LEVELS = {
    0: (22, 27, 34),    # #161b22 - Blank
    1: (14, 68, 41),    # #0e4429 - Level 1
    2: (0, 109, 50),    # #006d32 - Level 2
    3: (38, 166, 65),   # #26a641 - Level 3
    4: (57, 211, 83),   # #39d353 - Level 4
}


def parse_char_level(ch: str) -> int:
    """Map character to level (0-4)."""
    if ch in (' ', '0', '_'):
        return 0
    elif ch in ('.', '1', '-'):
        return 1
    elif ch in ('*', ':', '2'):
        return 2
    elif ch in ('#', '3', '+'):
        return 3
    elif ch in ('@', '4', '$'):
        return 4
    return 3


def load_ascii_file(filepath: str, cols: int = 52, rows: int = 7) -> List[List[int]]:
    """Loads a 7-line text file into a matrix."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\r\n') for line in f]
    matrix = [[0 for _ in range(cols)] for _ in range(rows)]
    for r in range(min(rows, len(lines))):
        line = lines[r]
        for c in range(min(cols, len(line))):
            matrix[r][c] = parse_char_level(line[c])
    return matrix


def display_preview(matrix: List[List[int]], title: str = ""):
    """Outputs visual ANSI preview directly in terminal."""
    print(f"\n┌── Canvas Preview: {title} " + "─" * max(2, 42 - len(title)) + "┐")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    header = [" "] * 52
    for i, m in enumerate(months):
        idx = min(52 - len(m), i * 4 + 1)
        for j, ch in enumerate(m):
            if idx + j < 52:
                header[idx + j] = ch

    print("     " + "".join(header))
    day_tags = {1: "Mon", 3: "Wed", 5: "Fri"}

    for r in range(7):
        prefix = f" {day_tags.get(r, '   ')} "
        print(prefix, end="")
        for c in range(52):
            lvl = matrix[r][c]
            r_c, g_c, b_c = COLOR_LEVELS.get(lvl, COLOR_LEVELS[0])
            print(f"\033[48;2;{r_c};{g_c};{b_c}m  \033[0m", end="")
        print()

    print("     " + " " * 32 + "Less ", end="")
    for lvl in range(5):
        r_c, g_c, b_c = COLOR_LEVELS[lvl]
        print(f"\033[48;2;{r_c};{g_c};{b_c}m  \033[0m", end="")
    print(" More")
    print("└──" + "─" * 65 + "┘\n")


def get_start_date(year: int = None, rolling: bool = False) -> datetime.date:
    """Finds starting Sunday for GitHub 52-week grid."""
    if rolling:
        today = datetime.date.today()
        cur_sun = today - datetime.timedelta(days=(today.weekday() + 1) % 7)
        return cur_sun - datetime.timedelta(weeks=51)
    target_year = year or datetime.date.today().year
    jan1 = datetime.date(target_year, 1, 1)
    offset = (jan1.weekday() + 1) % 7
    return jan1 - datetime.timedelta(days=offset)


def build_schedule(matrix: List[List[int]], start_sun: datetime.date, weights: Dict[int, int]) -> Dict[str, int]:
    """Generates day string to commit count map."""
    schedule = {}
    for col in range(52):
        for row in range(7):
            day = start_sun + datetime.timedelta(weeks=col, days=row)
            lvl = matrix[row][col]
            cnt = weights.get(lvl, 0)
            if cnt > 0:
                schedule[day.strftime('%Y-%m-%d')] = cnt
    return schedule


def run_fast_git_generation(schedule: Dict[str, int], repo_path: str, author_name: str, author_email: str, tz: str = "+0300") -> str:
    """Ultra-fast commit tree generation via git commit-tree."""
    if not os.path.exists(os.path.join(repo_path, '.git')):
        subprocess.run(['git', 'init', repo_path], check=True, capture_output=True)

    subprocess.run(['git', '-C', repo_path, 'config', 'user.name', author_name], check=True)
    subprocess.run(['git', '-C', repo_path, 'config', 'user.email', author_email], check=True)

    canvas_doc = os.path.join(repo_path, 'ACTIVITY.md')
    with open(canvas_doc, 'w', encoding='utf-8') as f:
        f.write("# Contribution Activity Canvas\n\nGenerated via Graph Artist tool.\n")

    subprocess.run(['git', '-C', repo_path, 'add', 'ACTIVITY.md'], check=True)
    tree_sha = subprocess.check_output(['git', '-C', repo_path, 'write-tree']).decode().strip()

    env = os.environ.copy()
    env['GIT_AUTHOR_NAME'] = author_name
    env['GIT_COMMITTER_NAME'] = author_name
    env['GIT_AUTHOR_EMAIL'] = author_email
    env['GIT_COMMITTER_EMAIL'] = author_email

    parent = None
    for day_str in sorted(schedule.keys()):
        count = schedule[day_str]
        for i in range(count):
            minute = (i * 2) % 60
            hour = 12 + ((i * 2) // 60)
            iso = f"{day_str}T{hour:02d}:{minute:02d}:00{tz}"
            env['GIT_AUTHOR_DATE'] = iso
            env['GIT_COMMITTER_DATE'] = iso

            cmd = ['git', '-C', repo_path, 'commit-tree', tree_sha, '-m', f"activity node {day_str} #{i+1}"]
            if parent:
                cmd.extend(['-p', parent])
            parent = subprocess.check_output(cmd, env=env).decode().strip()

    subprocess.run(['git', '-C', repo_path, 'update-ref', 'refs/heads/main', parent], check=True)
    subprocess.run(['git', '-C', repo_path, 'checkout', 'main', '-f'], check=True, capture_output=True)
    return parent
