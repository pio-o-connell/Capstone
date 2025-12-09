import os
import sys
from pathlib import Path


# Project root and paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Default remote DATABASE_URL (will be overridden by env var or CLI arg if provided)
DEFAULT_DATABASE_URL = (
    "postgresql://neondb_owner:npg_Jdzr3MEnZiN2@"
    "ep-patient-mountain-agw6c8sf.c-2.eu-central-1.aws.neon.tech/"
    "oil_shun_widow_111921"
)


def main(dump_path: str, database_url: str | None = None, dry_run: bool = False) -> int:
    # Ensure env var is set before Django imports settings
    if database_url:
        os.environ['DATABASE_URL'] = database_url
    os.environ.setdefault('DATABASE_URL', os.environ.get('DATABASE_URL', DEFAULT_DATABASE_URL))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    # Initialize Django
    import django

    try:
        django.setup()
    except Exception as e:
        print('Failed to setup Django:', e)
        return 2

    from django.conf import settings
    from django.db import connections
    from django.core.management import call_command

    print('Using database settings:')
    try:
        import json

        print(json.dumps(settings.DATABASES.get('default', {}), indent=2))
    except Exception:
        print(settings.DATABASES.get('default', {}))

    # Resolve dump file path relative to project root
    dump_file = PROJECT_ROOT / dump_path
    if not dump_file.exists():
        print(f'Dump file not found: {dump_file}')
        return 3

    # Quick DB connectivity check
    conn = connections['default']
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT version()')
            ver = cur.fetchone()
            print('DB server version:', ver)
    except Exception as e:
        print('Failed to connect/query DB:', e)
        return 4

    # Optional destructive operations: flush or drop
    # Respect dry-run and require explicit --confirm to execute.
    def do_flush(confirm: bool, dry_run: bool) -> bool:
        if dry_run or not confirm:
            print('\nDry-run: would run `manage.py flush --noinput` (this will delete ALL data).')
            return True
        try:
            print('\nRunning flush --noinput (deleting ALL data)')
            call_command('flush', '--noinput')
            print('Flush completed.')
            return True
        except Exception as e:
            print('Flush failed:', e)
            return False

    def do_drop(confirm: bool, dry_run: bool) -> bool:
        # Drop all tables in current DB schema (dangerous). Show list in dry-run.
        try:
            with conn.cursor() as cur:
                table_names = conn.introspection.table_names(cur)
        except Exception as e:
            print('Failed to introspect tables for drop:', e)
            return False

        if dry_run or not confirm:
            print(f"\nDry-run: would DROP {len(table_names)} tables. Example tables: {table_names[:10]}")
            return True

        print(f"Dropping {len(table_names)} tables (CASCADE). This is irreversible.")
        try:
            with conn.cursor() as cur:
                for t in table_names:
                    cur.execute(f'DROP TABLE IF EXISTS "{t}" CASCADE;')
            print('Drop completed.')
            return True
        except Exception as e:
            print('Drop failed:', e)
            return False

    # The caller will set these environment flags; read them here if present.
    # But we receive explicit flags from CLI below and will pass into main.

    # If dry-run is requested, parse fixture and simulate
    if dry_run:
        print(f'DRY-RUN: parsing {dump_file} and simulating import (no changes will be made)')
        import json
        from django.apps import apps
        total = 0
        will_create = 0
        will_update = 0
        unknown_natural = 0
        fk_issues = []

        # read bytes then try decoding with utf-8, falling back to replace or latin-1
        with open(dump_file, 'rb') as fh:
            raw = fh.read()
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text = raw.decode('utf-8', errors='replace')
                print('Warning: dump file contained invalid UTF-8 bytes; characters were replaced for parsing.')
            except Exception:
                text = raw.decode('latin-1')
                print('Warning: dump file decoded with latin-1 fallback.')
        data = json.loads(text)

        for obj in data:
            total += 1
            model_label = obj.get('model')
            pk = obj.get('pk')
            fields = obj.get('fields', {})
            if not model_label:
                continue
            try:
                app_label, model_name = model_label.split('.')
                model = apps.get_model(app_label, model_name)
            except Exception as e:
                # cannot resolve model
                fk_issues.append((model_label, 'model-not-found', str(e)))
                continue

            # Determine if object would be created or updated
            if pk is not None:
                try:
                    exists = model.objects.filter(pk=pk).exists()
                except Exception:
                    exists = False
                if exists:
                    will_update += 1
                else:
                    will_create += 1
            else:
                # natural keys or no pk provided
                unknown_natural += 1

                # Check foreign key references where possible
            for fname, fval in fields.items():
                try:
                    f = model._meta.get_field(fname)
                except Exception:
                    # field not on model (could be property or transformed name)
                    continue

                # ForeignKey/OneToOne
                if dry_run:
                    print(f'DRY-RUN: parsing {dump_file} and simulating import (no changes will be made)')
                    return _run_ordered_or_single_dry_run(dump_file)
    import argparse
    parser = argparse.ArgumentParser(description='Import dumpdata.json into remote Postgres')
    parser.add_argument('--dump', default='dumpdata.json', help='Path to dump file relative to project root')
    parser.add_argument('--database-url', default=None, help='Optional DATABASE_URL to use')
    parser.add_argument('--flush', action='store_true', help='Flush the database before import (destructive)')
    parser.add_argument('--drop', action='store_true', help='Drop all tables before import (very destructive)')
    parser.add_argument('--confirm', action='store_true', help='Confirm destructive actions (required to actually execute)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    args = parser.parse_args()

    # If the user requested flush/drop, run those first (dry-run unless --confirm provided)
    if args.flush or args.drop:
        # Set DATABASE_URL before initializing Django in main
        if args.database_url:
            os.environ['DATABASE_URL'] = args.database_url
        os.environ.setdefault('DATABASE_URL', os.environ.get('DATABASE_URL', DEFAULT_DATABASE_URL))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        import django
        try:
            django.setup()
        except Exception as e:
            print('Failed to setup Django for destructive ops:', e)
            sys.exit(2)

        from django.db import connections
        conn = connections['default']
        from django.core.management import call_command

        # Import helper functions from module-level by calling main with a special flag is simpler,
        # but we can replicate the helper logic here to avoid restructuring.
        def _do_flush(confirm: bool, dry_run: bool) -> bool:
            if dry_run or not confirm:
                print('\nDry-run: would run `manage.py flush --noinput` (this will delete ALL data).')
                return True
            try:
                print('\nRunning flush --noinput (deleting ALL data)')
                call_command('flush', '--noinput')
                print('Flush completed.')
                return True
            except Exception as e:
                print('Flush failed:', e)
                return False

        def _do_drop(confirm: bool, dry_run: bool) -> bool:
            try:
                with conn.cursor() as cur:
                    table_names = conn.introspection.table_names(cur)
            except Exception as e:
                print('Failed to introspect tables for drop:', e)
                return False

            if dry_run or not confirm:
                print(f"\nDry-run: would DROP {len(table_names)} tables. Example tables: {table_names[:10]}")
                return True

            print(f"Dropping {len(table_names)} tables (CASCADE). This is irreversible.")
            try:
                with conn.cursor() as cur:
                    for t in table_names:
                        cur.execute(f'DROP TABLE IF EXISTS "{t}" CASCADE;')
                print('Drop completed.')
                return True
            except Exception as e:
                print('Drop failed:', e)
                return False

        ok = True
        if args.flush:
            ok = ok and _do_flush(args.confirm, args.dry_run)
        if args.drop:
            ok = ok and _do_drop(args.confirm, args.dry_run)

        if not ok:
            print('Destructive operation failed or was cancelled. Aborting import.')
            sys.exit(6)

    exit_code = main(args.dump, args.database_url, args.dry_run)
    sys.exit(exit_code)


def _run_ordered_or_single_dry_run(dump_file_path: Path) -> int:
    """Run a dry-run. If CLI asked for ordered sequencing (via env/args), it's handled at module level.
    This function will parse the fixture and run a simulated import in the order:
    contenttypes -> auth -> users -> rest. It prints detailed attempted lookups for user natural keys.
    """
    import json
    from django.apps import apps as django_apps

    # load the fixture
    try:
        with open(dump_file_path, 'rb') as fh:
            raw = fh.read()
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            text = raw.decode('utf-8', errors='replace')
    except Exception as e:
        print('Failed to read dump file for dry-run:', e)
        return 3

    try:
        data = json.loads(text)
    except Exception as e:
        print('Failed to parse dump JSON:', e)
        return 3

    # Group objects by app label
    by_app = {}
    for obj in data:
        model_label = obj.get('model')
        if not model_label or '.' not in model_label:
            continue
        app_label, model_name = model_label.split('.')
        by_app.setdefault(app_label, []).append(obj)

    # Determine app order: prefer contenttypes, auth, users
    ordered = []
    for a in ('contenttypes', 'auth', 'users'):
        if a in by_app:
            ordered.append(a)
    # then the rest
    for a in sorted(by_app.keys()):
        if a not in ordered:
            ordered.append(a)

    # Track simulated existence: set of (app_label, model_name, pk)
    simulated_existing = set()
    # Also track natural-key maps per model: {(app_label, ModelName): {('username',val): pk}}
    natural_maps = {}

    def _record_created(model_label, pk, fields):
        app_label, model_name = model_label.split('.')
        simulated_existing.add((app_label, model_name, pk))
        key = (app_label, model_name)
        natural_maps.setdefault(key, {})
        # store username/email if available
        if isinstance(fields, dict):
            for candidate in ('username', 'email'):
                if candidate in fields:
                    natural_maps[key][(candidate, fields[candidate])] = pk

    # Helper to check existence: consult DB and simulated_existing
    from django.db import connections
    conn = connections['default']

    def exists_in_db_or_sim(app_label, model_name, pk):
        if (app_label, model_name, pk) in simulated_existing:
            return True
        try:
            model = django_apps.get_model(app_label, model_name)
            return model.objects.filter(pk=pk).exists()
        except Exception:
            return False

    # Simulate per-app
    total = 0
    overall_create = 0
    overall_update = 0
    overall_unknown = 0
    overall_fk_issues = []

    for app_label in ordered:
        objs = by_app.get(app_label, [])
        print(f"\n--- Dry-run for app: {app_label} (objects: {len(objs)}) ---")
        created = 0
        updated = 0
        unknown = 0
        fk_issues = []

        for obj in objs:
            total += 1
            model_label = obj.get('model')
            pk = obj.get('pk')
            fields = obj.get('fields', {})
            try:
                app_l, model_name = model_label.split('.')
                model = django_apps.get_model(app_l, model_name)
            except Exception as e:
                fk_issues.append((model_label, 'model-not-found', str(e)))
                continue

            if pk is not None:
                if exists_in_db_or_sim(app_l, model_name, pk):
                    updated += 1
                else:
                    created += 1
                    _record_created(model_label, pk, fields)
            else:
                unknown += 1

            # Check FKs similar to earlier logic but consult simulated_existing & natural_maps
            for fname, fval in fields.items():
                try:
                    f = model._meta.get_field(fname)
                except Exception:
                    continue

                if getattr(f, 'remote_field', None) and not f.many_to_many:
                    target = f.remote_field.model
                    try:
                        target_app = target._meta.app_label
                        target_model_name = target._meta.model_name
                    except Exception:
                        target_app = None
                        target_model_name = None

                    if fval is None:
                        continue

                    # natural key list -> try resolve by natural_maps or manager
                    if isinstance(fval, (list, tuple)):
                        resolved = False
                        # ContentType special-case
                        try:
                            from django.contrib.contenttypes.models import ContentType
                            if target_app == 'contenttypes' and len(fval) >= 2:
                                if ContentType.objects.filter(app_label=fval[0], model=fval[1]).exists() or \
                                   ((fval[0], fval[1],) in natural_maps.get((target_app, target_model_name), {})):
                                    resolved = True
                                else:
                                    fk_issues.append((model_label, pk, fname, fval, 'fk-missing-contenttype'))
                                    resolved = True
                        except Exception:
                            pass

                        if not resolved:
                            # try manager.get_by_natural_key
                            try:
                                mgr = getattr(target, '_default_manager', None)
                                if mgr and hasattr(mgr, 'get_by_natural_key'):
                                    try:
                                        mgr.get_by_natural_key(*fval)
                                        resolved = True
                                    except Exception:
                                        pass
                            except Exception:
                                pass

                        # check natural_maps (simulated creations)
                        if not resolved and target_app and target_model_name:
                            nm = natural_maps.get((target_app, target_model_name), {})
                            # try single-value natural keys against username/email
                            if len(fval) == 1:
                                single = fval[0]
                                for fld in ('username', 'email'):
                                    if (fld, single) in nm:
                                        resolved = True
                                        break

                        if not resolved:
                            fk_issues.append((model_label, pk, fname, fval, 'fk-naturalkey-missing-detailed'))
                        continue

                    # scalar PK check consult db + simulated
                    if target_app and target_model_name:
                        if not exists_in_db_or_sim(target_app, target_model_name, fval):
                            fk_issues.append((model_label, pk, fname, fval, 'fk-missing'))
                    else:
                        fk_issues.append((model_label, pk, fname, fval, 'fk-check-error'))

                if f.many_to_many:
                    if not isinstance(fval, (list, tuple)):
                        continue
                    for m2m_pk in fval:
                        try:
                            target_model = f.remote_field.model
                            ta = target_model._meta.app_label
                            tm = target_model._meta.model_name
                            if not exists_in_db_or_sim(ta, tm, m2m_pk):
                                fk_issues.append((model_label, pk, fname, m2m_pk, 'm2m-missing'))
                        except Exception:
                            fk_issues.append((model_label, pk, fname, m2m_pk, 'm2m-check-error'))

        overall_create += created
        overall_update += updated
        overall_unknown += unknown
        overall_fk_issues.extend(fk_issues)

        print(f'  Would create: {created}, Would update: {updated}, Unknown/natural: {unknown}, FK issues: {len(fk_issues)}')
        if fk_issues:
            print('  Examples:')
            for i, it in enumerate(fk_issues[:20], 1):
                print('   ', i, it)

    # Summary
    print('\nDRY-RUN COMPLETE: overall summary')
    print(f'  Total objects in fixture: {total}')
    print(f'  Would create: {overall_create}')
    print(f'  Would update: {overall_update}')
    print(f'  Unknown (natural keys/no pk): {overall_unknown}')
    print(f'  FK issues found: {len(overall_fk_issues)}')
    if overall_fk_issues:
        print('  First examples:')
        for i, it in enumerate(overall_fk_issues[:50], 1):
            print('   ', i, it)

    return 0
