r"""Wrapper to run `DB-scripts/create_posts_comments_v2.py` against the remote Postgres DB.
Performs a dry-run by default (wraps operations in a transaction and rolls back).

Usage (dry-run):
  .venv\Scripts\python.exe DB-scripts\create-postgres-post_comments_v2.py

To actually commit changes:
  .venv\Scripts\python.exe DB-scripts\create-postgres-post_comments_v2.py --commit
"""
from pathlib import Path
import os
import sys
import runpy

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_DATABASE_URL = (
    "postgresql://neondb_owner:npg_Jdzr3MEnZiN2@"
    "ep-patient-mountain-agw6c8sf.c-2.eu-central-1.aws.neon.tech/"
    "oil_shun_widow_111921"
)


def main(commit: bool = False):
    os.environ.setdefault('DATABASE_URL', os.environ.get('DATABASE_URL', DEFAULT_DATABASE_URL))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    import django
    from django.db import transaction, connections

    django.setup()

    print('Using DATABASE_URL=', os.environ['DATABASE_URL'])
    print('DB connection settings:', connections['default'].settings_dict)

    script_path = str(Path(__file__).resolve().parent / 'create_posts_comments_v2.py')

    try:
        with transaction.atomic():
            print('Starting dry-run transaction (will rollback unless --commit given)')
            # Run the posts/comments script but avoid leaking this wrapper's CLI args
            old_argv = sys.argv[:]
            try:
                sys.argv = [script_path]
                runpy.run_path(script_path, run_name='__main__')
            finally:
                sys.argv = old_argv
            if commit:
                print('Commit requested: leaving transaction to commit')
            else:
                print('Dry-run: rolling back transaction')
                transaction.set_rollback(True)
    except Exception as e:
        print('Script raised exception:', e)
        print('Dry-run wrapper will ensure rollback (if possible).')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--commit', action='store_true', help='Actually commit DB changes (dangerous)')
    args = parser.parse_args()
    main(commit=args.commit)
