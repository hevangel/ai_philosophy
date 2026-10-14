"""Load portal credentials from the repo-root .env (gitignored, never committed).

Usage:
    from portal_env import get
    email = get('PHILPAPERS_EMAIL')

CLI (prints the value; keys only when no argument given):
    py -3 publish/scripts/portal_env.py PHILPAPERS_EMAIL
"""
from pathlib import Path


def load_env():
    env = {}
    p = Path(__file__).resolve().parents[2] / '.env'
    if not p.exists():
        return env
    for line in p.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip()
    return env


def get(name):
    return load_env().get(name)


if __name__ == '__main__':
    import sys
    env = load_env()
    if len(sys.argv) > 1:
        print(env.get(sys.argv[1], ''))
    else:
        print(' '.join(sorted(env)))
