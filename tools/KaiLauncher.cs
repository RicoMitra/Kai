using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;
using System.Runtime.InteropServices;

internal static class KaiLauncher {
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern uint GetFileAttributes(string path);
    private static string Inspect(string path) {
        uint attributes = GetFileAttributes(path);
        int error = attributes == uint.MaxValue ? Marshal.GetLastWin32Error() : 0;
        string detail = path + "\nFile.Exists=" + File.Exists(path) + "; attributes=" + attributes + "; Win32=" + error;
        try { using (FileStream file = File.Open(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite)) detail += "; readable=" + file.Length; }
        catch (Exception ex) { detail += "; " + ex.GetType().Name + ": " + ex.Message; }
        return detail;
    }
    private static int Missing(string message, string path, bool check, int code) {
        if (check) return code;
        string details = message + "\n\n" + path;
        try {
            string logs = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Kai", "logs");
            Directory.CreateDirectory(logs);
            File.WriteAllText(Path.Combine(logs, "launcher.log"), DateTimeOffset.Now.ToString("o") + "\n" + details + "\n" + Inspect(path));
        } catch (IOException) { } catch (UnauthorizedAccessException) { }
        MessageBox.Show(details, "Unable to open Kai", MessageBoxButtons.OK, MessageBoxIcon.Information);
        return code;
    }

    [STAThread]
    private static int Main(string[] args) {
        string root = AppDomain.CurrentDomain.BaseDirectory;
        string local = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        string python = Path.Combine(local, "Kai", "runtime", "Scripts", "pythonw.exe");
        string runtimeLocal = null;
        // MSIX redirects AppData writes made during setup inside Codex. Explorer
        // cannot see that virtual path, so use its existing physical location.
        if (!File.Exists(python)) {
            string packages = Path.Combine(local, "Packages");
            if (Directory.Exists(packages)) {
                foreach (string package in Directory.GetDirectories(packages, "OpenAI.Codex_*")) {
                    string candidateLocal = Path.Combine(package, "LocalCache", "Local");
                    string candidate = Path.Combine(candidateLocal, "Kai", "runtime", "Scripts", "pythonw.exe");
                    if (File.Exists(candidate)) { python = candidate; runtimeLocal = candidateLocal; break; }
                }
            }
        }
        string entry = Path.Combine(root, "kai", "start.pyw");
        bool check = Array.IndexOf(args, "--check") >= 0;
        if (Array.IndexOf(args, "--diagnose") >= 0) {
            string logs = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Kai", "logs");
            Directory.CreateDirectory(logs);
            File.WriteAllText(Path.Combine(logs, "launcher-diagnostic.log"), "64bit=" + Environment.Is64BitProcess + "\n" + Inspect(python) + "\n" + Inspect(entry));
            return 0;
        }
        if (!File.Exists(python))
            return Missing("Kai Python runtime is missing. Run Setup Kai from the application folder.", python, check, 2);
        if (!File.Exists(entry))
            return Missing("Kai application files are missing. Open Kai from its complete folder or Desktop shortcut. For OneDrive folders, make sure the files are available on this device.", entry, check, 3);
        if (check) return 0;
        string flags = "";
        foreach (string arg in args) {
            if (arg == "--demo" || arg == "--reduced-motion" || arg == "--media-on-demand") flags += " " + arg;
        }
        try {
            ProcessStartInfo start = new ProcessStartInfo {
                FileName = python, Arguments = "-B \"" + entry + "\"" + flags,
                WorkingDirectory = Path.Combine(root, "kai"),
                UseShellExecute = false, CreateNoWindow = true
            };
            // Keep the existing settings, Spotify token and database together.
            if (runtimeLocal != null) start.EnvironmentVariables["LOCALAPPDATA"] = runtimeLocal;
            Process.Start(start);
            return 0;
        } catch (Exception error) {
            MessageBox.Show(error.Message, "Unable to open Kai", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }
}
