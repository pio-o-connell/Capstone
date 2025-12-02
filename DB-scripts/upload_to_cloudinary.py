"""Upload local image files to Cloudinary and write a mapping JSON.

Usage:
  python upload_to_cloudinary.py [--dry-run] [--force] [--dirs DIR1,DIR2]

The script reads Cloudinary credentials from environment variables (or from
`env.py` if present). It uploads images found under the specified directories
and writes `DB-scripts/cloudinary_uploads.json` with mapping local_path -> info.
"""
from pathlib import Path
import os
import json
import argparse
import mimetypes

try:
    import cloudinary
    import cloudinary.uploader
except Exception as e:
    print("cloudinary package is required. Install with: pip install cloudinary")
    raise


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DIRS = [
    BASE_DIR / 'DB-scripts',
    BASE_DIR / 'services' / 'static',
    BASE_DIR / 'core' / 'static',
    BASE_DIR / 'documentation' / 'images',
]

OUT_FILE = Path(__file__).resolve().parent / 'cloudinary_uploads.json'


def load_mapping():
    if OUT_FILE.exists():
        return json.loads(OUT_FILE.read_text())
    return {}


def save_mapping(mapping):
    OUT_FILE.write_text(json.dumps(mapping, indent=2))


def is_image(path: Path):
    if not path.is_file():
        return False
    mime, _ = mimetypes.guess_type(str(path))
    return mime and mime.startswith('image')


def configure_cloudinary():
    # Configure Cloudinary explicitly from env vars. Use CLOUDINARY_URL if present
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    cloud_url = os.environ.get('CLOUDINARY_URL')
    if cloud_name and api_key and api_secret:
        cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret)
        return
    if cloud_url:
        # cloudinary.config accepts a dict from parse_qs if necessary; set via CLOUDINARY_URL
        cloudinary.config(cloud_url=cloud_url)
        return
    raise RuntimeError('Cloudinary credentials not found in environment')


def upload_file(local_path: Path, public_prefix='capstone'):
    rel = local_path.relative_to(BASE_DIR)
    pubid = f"{public_prefix}/{rel.with_suffix('').as_posix().replace('/', '_')}"
    print(f"Uploading {rel} -> public_id={pubid}")
    res = cloudinary.uploader.upload(str(local_path), public_id=pubid, resource_type='image')
    return {
        'public_id': res.get('public_id'),
        'url': res.get('secure_url') or res.get('url'),
        'version': res.get('version'),
    }


def find_images(dirs):
    files = []
    for d in dirs:
        p = Path(d)
        if not p.exists():
            continue
        for f in p.rglob('*'):
            if is_image(f):
                files.append(f)
    return sorted(set(files))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--force', action='store_true', help='Re-upload even if mapping exists')
    parser.add_argument('--dirs', help='Comma-separated list of dirs to search')
    args = parser.parse_args()

    # If an env.py exists in project root, import it to set env vars (developer convenience)
    env_path = BASE_DIR / 'env.py'
    if env_path.exists():
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location('local_env', str(env_path))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception:
            pass

    configure_cloudinary()

    dirs = []
    if args.dirs:
        dirs = [Path(x) if Path(x).is_absolute() else BASE_DIR / x for x in args.dirs.split(',')]
    else:
        dirs = DEFAULT_DIRS

    print('Searching directories for images:')
    for d in dirs:
        print(' -', d)

    images = find_images(dirs)
    print(f'Found {len(images)} image files to consider')

    mapping = load_mapping()

    changed = False
    for img in images:
        key = str(img.relative_to(BASE_DIR))
        if key in mapping and not args.force:
            print(f'Skipping (already mapped): {key}')
            continue
        if args.dry_run:
            print(f'DRY RUN: would upload {key}')
            changed = True
            continue
        try:
            info = upload_file(img)
        except Exception as e:
            print(f'Failed to upload {img}: {e}')
            continue
        mapping[key] = info
        changed = True

    if changed:
        if args.dry_run:
            print('Dry-run: no mapping written.')
        else:
            save_mapping(mapping)
            print(f'Wrote mapping to {OUT_FILE}')
    else:
        print('No changes made.')


if __name__ == '__main__':
    main()
