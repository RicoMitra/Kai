"""Check launcher path resolution and missing-entry classification without dialogs."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory() as directory:
        work=Path(directory)
        result=subprocess.run([str(ROOT/'Kai.exe'),'--check'],cwd=work)
        assert result.returncode==0,result.returncode
        isolated=work/'Kai.exe';shutil.copy2(ROOT/'Kai.exe',isolated)
        result=subprocess.run([str(isolated),'--check'],cwd=ROOT)
        assert result.returncode==3,result.returncode
    report={'project_launcher_from_other_cwd':True,'missing_app_entry_code':3,
            'missing_runtime_code':2,'explorer_launch':'requires direct user verification; Codex inherits MSIX filesystem redirection','scope':'Installed runtime exists; copied launcher alone lacks start.pyw. Missing runtime branch inspected, not simulated.'}
    target=ROOT/'artifacts/redesign/launcher-verification.json'
    target.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
