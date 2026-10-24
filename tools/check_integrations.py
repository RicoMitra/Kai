import json, os, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path.cwd()/'kai'))
from tasks import invoke

def main():
    result = {}
    previous = os.environ.get('LOCALAPPDATA')
    try:
        with tempfile.TemporaryDirectory() as temporary:
            os.environ['LOCALAPPDATA'] = temporary
            for name, args in [('weather', ('London',)), ('lyrics', ('Blinding Lights', 'The Weeknd', 200)), ('system', ())]:
                try:
                    value = invoke(name, *args)
                    if name == 'weather':
                        result[name] = {'ok': isinstance(value.get('temperature'), (int, float)), 'test_city_only': True}
                    elif name == 'lyrics':
                        result[name] = {'ok': bool(value['plain'] or value['synced']), 'synced_lines': len(value['synced'])}
                    else:
                        result[name] = {'ok': all(key in value for key in ('CPU', 'RAM', 'Baterai', 'GPU')), 'sensors_may_be_unavailable': True}
                except Exception as exc:
                    result[name] = {'ok': False, 'error': str(exc)}
    finally:
        if previous is not None: os.environ['LOCALAPPDATA'] = previous
        else: os.environ.pop('LOCALAPPDATA', None)
    Path('artifacts/island/integrations-verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
