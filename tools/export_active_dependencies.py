"""Export installed versions for the active requirements closure, not unrelated global packages."""
import argparse
import importlib.metadata as metadata
from pathlib import Path
try:
    from packaging.requirements import Requirement
except ImportError:
    from pip._vendor.packaging.requirements import Requirement

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    queue=[Requirement(line.strip()) for line in (ROOT/'kai/requirements.txt').read_text().splitlines() if line.strip() and not line.startswith('#')]
    seen=set();packages={}
    while queue:
        request=queue.pop();key=(request.name.lower().replace('_','-'),tuple(sorted(request.extras)))
        if key in seen:continue
        seen.add(key);distribution=metadata.distribution(request.name)
        packages[distribution.metadata['Name']]=distribution.version
        for declaration in distribution.requires or []:
            child=Requirement(declaration)
            if child.marker is None or any(child.marker.evaluate({'extra':extra}) for extra in (request.extras or {''})):queue.append(child)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text('\n'.join(f'{name}=={version}' for name,version in sorted(packages.items()))+'\n',encoding='utf-8')
    print(f'Exported {len(packages)} active installed Python packages for audit')


if __name__=='__main__':main()
