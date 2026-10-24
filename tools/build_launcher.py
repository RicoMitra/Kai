"""Lossless logo format/size conversion and native Windows GUI launcher build."""
from pathlib import Path
import os
import struct
import subprocess
import sys
import tempfile

from PySide6.QtCore import QByteArray, QBuffer, QIODevice, Qt
from PySide6.QtGui import QImage

ROOT = Path(__file__).resolve().parents[1]


def main():
    assets = ROOT / 'assets'
    source = QImage(str(assets / 'kai-original.png'))
    if source.isNull(): raise RuntimeError('Logo Kai tidak terbaca')
    frames = []
    for size in (16, 20, 24, 32, 40, 48, 64, 128, 256):
        image = source.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        buffer = QBuffer(); buffer.open(QIODevice.WriteOnly)
        image.save(buffer, 'PNG')
        frames.append((size, bytes(buffer.data())))
        if size in (64, 128): image.save(str(assets / f'kai-{size}.png'))
    offset = 6 + 16 * len(frames)
    icon = struct.pack('<HHH', 0, 1, len(frames))
    for size, data in frames:
        icon += struct.pack('<BBBBHHII', size % 256, size % 256, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    icon += b''.join(data for _, data in frames)
    (assets / 'kai.ico').write_bytes(icon)
    compiler = Path(os.environ['WINDIR']) / 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
    with tempfile.TemporaryDirectory(prefix='kai-launcher-') as directory:
        executable = Path(directory) / 'Kai.exe'
        subprocess.run([str(compiler), '/nologo', '/target:winexe', '/optimize+',
                        '/reference:System.Windows.Forms.dll', '/win32icon:' + str(assets / 'kai.ico'),
                        '/out:' + str(executable), str(ROOT / 'tools/KaiLauncher.cs')], check=True)
        os.replace(executable, ROOT / 'Kai.exe')
    subprocess.run([str(ROOT / 'Kai.exe'), '--check'], check=True)
    print('Kai.exe dibuat: GUI subsystem, ikon robot, tanpa shell/console.')


if __name__ == '__main__': main()
