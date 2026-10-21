// Double-click launcher for the Shiny screening app.
//
//   csc /target:winexe /out:RunScreeningApp.exe app\launcher\RunScreeningApp.cs
//
// A Shiny app is a local web server, so something has to render HTML. This starts R on a free
// port with no console, waits for the port to answer, then opens Edge or Chrome in app mode:
// one window, no tabs and no address bar, which is what people mean by "an application".
// Closing that window stops R. If R never comes up, its output goes into the error box rather
// than vanishing with a console nobody saw.
using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using Microsoft.Win32;
using System.Windows.Forms;

class RunScreeningApp
{
    const string PROJECT_FILE = "BIN381-P1.Rproj";
    const string LIBRARY_PROBE = @"renv\library\windows\R-4.6\x86_64-w64-mingw32\shiny\DESCRIPTION";
    const int STARTUP_SECONDS = 120;        // a cold start loads the model and the tidymodels stack

    static void Complain(string title, string message)
    {
        MessageBox.Show(message, title, MessageBoxButtons.OK, MessageBoxIcon.Warning);
    }

    static string FindProjectRoot()
    {
        DirectoryInfo dir = new DirectoryInfo(Path.GetDirectoryName(Application.ExecutablePath));
        while (dir != null)
        {
            if (File.Exists(Path.Combine(dir.FullName, PROJECT_FILE))) return dir.FullName;
            dir = dir.Parent;
        }
        return null;
    }

    static string FromRegistry(RegistryKey hive, string path)
    {
        using (RegistryKey key = hive.OpenSubKey(path))
        {
            return key == null ? null : key.GetValue("InstallPath") as string;
        }
    }

    static string FirstFile(string folder, params string[] relatives)
    {
        if (string.IsNullOrEmpty(folder)) return null;
        foreach (string rel in relatives)
        {
            string full = Path.Combine(folder, rel);
            if (File.Exists(full)) return full;
        }
        return null;
    }

    static string FindRscript()
    {
        foreach (string home in new string[] {
            FromRegistry(Registry.CurrentUser, @"SOFTWARE\R-core\R"),
            FromRegistry(Registry.LocalMachine, @"SOFTWARE\R-core\R"),
            FromRegistry(Registry.LocalMachine, @"SOFTWARE\WOW6432Node\R-core\R") })
        {
            string exe = FirstFile(home, @"bin\x64\Rscript.exe", @"bin\Rscript.exe");
            if (exe != null) return exe;
        }
        foreach (string root in new string[] {
            @"C:\Program Files\R", @"C:\Program Files (x86)\R", @"C:\R" })
        {
            if (!Directory.Exists(root)) continue;
            string[] versions = Directory.GetDirectories(root);
            Array.Sort(versions);
            Array.Reverse(versions);                       // newest R first
            foreach (string v in versions)
            {
                string exe = FirstFile(v, @"bin\x64\Rscript.exe", @"bin\Rscript.exe");
                if (exe != null) return exe;
            }
        }
        return null;
    }

    // Edge ships with Windows, so this nearly always finds something.
    static string FindAppModeBrowser()
    {
        string pf = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles);
        string pf86 = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86);
        string local = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        foreach (string candidate in new string[] {
            FirstFile(pf86, @"Microsoft\Edge\Application\msedge.exe"),
            FirstFile(pf, @"Microsoft\Edge\Application\msedge.exe"),
            FirstFile(pf, @"Google\Chrome\Application\chrome.exe"),
            FirstFile(pf86, @"Google\Chrome\Application\chrome.exe"),
            FirstFile(local, @"Google\Chrome\Application\chrome.exe") })
        {
            if (candidate != null) return candidate;
        }
        return null;
    }

    // R picks its own port and prints "Listening on http://127.0.0.1:PORT". Reading that back
    // is both the readiness signal and the address: there is no window in which this launcher
    // holds a port that R has not bound yet, so nothing else can take it in between and be
    // opened in a window titled like ours.
    static readonly Regex LISTENING =
        new Regex(@"Listening on (http://127\.0\.0\.1:\d+)", RegexOptions.IgnoreCase);

    static string WaitForUrl(StringBuilder log, Process r)
    {
        for (int i = 0; i < STARTUP_SECONDS * 2; i++)
        {
            string seen;
            lock (log) { seen = log.ToString(); }
            Match m = LISTENING.Match(seen);
            if (m.Success) return m.Groups[1].Value;
            if (r.HasExited) return null;          // died early; the caller shows its output
            Thread.Sleep(500);
        }
        return null;
    }

    [STAThread]
    static int Main()
    {
        string root = FindProjectRoot();
        if (root == null)
        {
            Complain("Project not found",
                "This launcher has to sit inside the BIN381-P1 project folder, next to " +
                PROJECT_FILE + " or somewhere under it.\n\nIt is currently in:\n" +
                Path.GetDirectoryName(Application.ExecutablePath));
            return 1;
        }

        string rscript = FindRscript();
        if (rscript == null)
        {
            Complain("R is not installed",
                "The screening app is an R/Shiny app, so it needs R itself - this launcher only " +
                "starts it.\n\nInstall R 4.6.1 from https://cran.r-project.org, then open " +
                PROJECT_FILE + " once and run:\n\n    renv::restore()\n\nAfter that, this " +
                "launcher will work.");
            return 2;
        }

        if (!File.Exists(Path.Combine(root, LIBRARY_PROBE)))
        {
            Complain("The project packages are not installed",
                "R is installed, but this project's library has no shiny in it.\n\nOpen " +
                PROJECT_FILE + " in RStudio and run:\n\n    renv::install(c(\"shiny\", " +
                "\"bslib\", \"DT\", \"workflows\", \"glmnet\", \"recipes\", \"parsnip\", " +
                "\"hardhat\"), type = \"binary\")\n\nThat is enough to run the app. The full " +
                "renv::restore() also needs Rtools - see the README.");
            return 3;
        }

        ProcessStartInfo start = new ProcessStartInfo(rscript,
            "-e \"shiny::runApp('app', host = '127.0.0.1', launch.browser = FALSE)\"");
        start.WorkingDirectory = root;      // .Rprofile activates renv; app.R resolves ../models
        start.UseShellExecute = false;
        start.CreateNoWindow = true;
        start.RedirectStandardOutput = true;
        start.RedirectStandardError = true;

        StringBuilder log = new StringBuilder();
        DataReceivedEventHandler collect = delegate(object sender, DataReceivedEventArgs e)
        {
            if (e.Data != null) lock (log) { log.AppendLine(e.Data); }
        };

        Process r;
        try
        {
            r = Process.Start(start);
            r.OutputDataReceived += collect;      // drained, or a full pipe would stall R
            r.ErrorDataReceived += collect;
            r.BeginOutputReadLine();
            r.BeginErrorReadLine();
        }
        catch (Exception e)
        {
            Complain("Could not start R", "R was found at:\n" + rscript + "\n\nbut would not " +
                "start:\n" + e.Message);
            return 4;
        }

        string url = WaitForUrl(log, r);
        if (url == null)
        {
            string tail;
            lock (log) { tail = log.ToString(); }
            if (tail.Length > 1500) tail = tail.Substring(tail.Length - 1500);
            try { if (!r.HasExited) r.Kill(); } catch { }
            Complain("The app did not start",
                "R ran but never reported a listening address.\n\nWhat R said:\n\n" +
                (tail.Length == 0 ? "(nothing)" : tail));
            return 5;
        }

        string browser = FindAppModeBrowser();
        if (browser == null)
        {
            Process.Start(url);               // no Edge or Chrome: ordinary browser, R left running
            return 0;
        }

        // Its own profile folder, so the window is its own process and closing it means closing
        // the app rather than detaching into an already-running browser.
        string profile = Path.Combine(Path.GetTempPath(), "bin381-screening-app-window");
        Process window = Process.Start(browser,
            "--app=" + url + " --window-size=1280,900 --user-data-dir=\"" + profile + "\"");
        if (window != null) window.WaitForExit();
        try { if (!r.HasExited) r.Kill(); } catch { }
        return 0;
    }
}
