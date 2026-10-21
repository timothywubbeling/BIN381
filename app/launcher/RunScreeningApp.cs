// Double-click launcher for the Shiny screening app.
//
//   csc /target:winexe /out:RunScreeningApp.exe app\launcher\RunScreeningApp.cs
//
// It finds R, finds the project, and runs `shiny::runApp("app")` with the project root as the
// working directory, so .Rprofile activates renv and the model path inside app.R resolves.
// It cannot install anything: R and the project library have to be there, and the point of the
// checks below is to say which one is missing instead of failing in a console that disappears.
using System;
using System.Diagnostics;
using System.IO;
using Microsoft.Win32;
using System.Windows.Forms;

class RunScreeningApp
{
    const string PROJECT_FILE = "BIN381-P1.Rproj";
    const string LIBRARY_PROBE = @"renv\library\windows\R-4.6\x86_64-w64-mingw32\shiny\DESCRIPTION";

    static void Complain(string title, string message)
    {
        MessageBox.Show(message, title, MessageBoxButtons.OK, MessageBoxIcon.Warning);
    }

    // The exe may sit at the project root or anywhere under it.
    static string FindProjectRoot()
    {
        DirectoryInfo dir = new DirectoryInfo(
            Path.GetDirectoryName(Application.ExecutablePath));
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
            if (key == null) return null;
            return key.GetValue("InstallPath") as string;
        }
    }

    static string FindRscript()
    {
        foreach (string home in new string[] {
            FromRegistry(Registry.CurrentUser, @"SOFTWARE\R-core\R"),
            FromRegistry(Registry.LocalMachine, @"SOFTWARE\R-core\R"),
            FromRegistry(Registry.LocalMachine, @"SOFTWARE\WOW6432Node\R-core\R") })
        {
            if (string.IsNullOrEmpty(home)) continue;
            foreach (string sub in new string[] { @"bin\x64\Rscript.exe", @"bin\Rscript.exe" })
            {
                string exe = Path.Combine(home, sub);
                if (File.Exists(exe)) return exe;
            }
        }
        // Installed without writing the registry, or a portable copy: take the newest R-*.
        foreach (string root in new string[] {
            @"C:\Program Files\R", @"C:\Program Files (x86)\R", @"C:\R" })
        {
            if (!Directory.Exists(root)) continue;
            string[] versions = Directory.GetDirectories(root);
            Array.Sort(versions);
            Array.Reverse(versions);
            foreach (string v in versions)
            {
                foreach (string sub in new string[] { @"bin\x64\Rscript.exe", @"bin\Rscript.exe" })
                {
                    string exe = Path.Combine(v, sub);
                    if (File.Exists(exe)) return exe;
                }
            }
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
                "R is installed, but this project's library is empty, so shiny and the model " +
                "packages are missing.\n\nOpen " + PROJECT_FILE + " in RStudio and run:\n\n" +
                "    renv::restore()\n\nThat installs the 169 packages pinned in renv.lock. It " +
                "only has to be done once per machine, and it is not quick.");
            return 3;
        }

        // A visible console: if R fails (a missing package, a locked port), the reason stays on
        // screen instead of disappearing with the window.
        ProcessStartInfo start = new ProcessStartInfo(rscript,
            "-e \"cat('Starting the household food-insecurity screening app...\\n'); " +
            "shiny::runApp('app', launch.browser = TRUE)\"");
        start.WorkingDirectory = root;      // .Rprofile activates renv; app.R resolves ../models
        start.UseShellExecute = false;
        try
        {
            Process.Start(start);
        }
        catch (Exception e)
        {
            Complain("Could not start R", "R was found at:\n" + rscript + "\n\nbut would not " +
                "start:\n" + e.Message);
            return 4;
        }
        return 0;
    }
}
