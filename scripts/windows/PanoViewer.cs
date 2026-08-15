using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Windows.Forms;
using System.Reflection;

[assembly: AssemblyTitle("PanoViewer")]
[assembly: AssemblyDescription("Offline 360° panorama viewer")]
[assembly: AssemblyCompany("Liang Xiaohui")]
[assembly: AssemblyProduct("PanoViewer")]
[assembly: AssemblyCopyright("Copyright © 2026 Liang Xiaohui (梁晓辉)")]
[assembly: AssemblyVersion("__APP_VERSION__.0")]
[assembly: AssemblyFileVersion("__APP_VERSION__.0")]

internal static class PanoViewerApp
{
    [STAThread]
    private static int Main(string[] args)
    {
        try
        {
            string image = args.Length > 0 ? args[0] : ChooseImage();
            if (String.IsNullOrEmpty(image)) return 0;
            image = Path.GetFullPath(image);
            if (!File.Exists(image)) throw new FileNotFoundException("找不到图片。", image);

            string mime = GetMime(Path.GetExtension(image));
            byte[] bytes = File.ReadAllBytes(image);
            string dataUrl = "data:" + mime + ";base64," + Convert.ToBase64String(bytes);
            string template = ReadTemplate();
            string html = template.Replace("__EMBEDDED_IMAGE__", dataUrl);

            string outputDir = Path.Combine(Path.GetTempPath(), "PanoViewer");
            Directory.CreateDirectory(outputDir);
            string output = Path.Combine(outputDir, "viewer-" + Process.GetCurrentProcess().Id + ".html");
            File.WriteAllText(output, html, new UTF8Encoding(false));
            Process.Start(new ProcessStartInfo(output) { UseShellExecute = true });
            return 0;
        }
        catch (Exception ex)
        {
            MessageBox.Show(ex.Message, "PanoViewer __APP_VERSION__", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }

    private static string ChooseImage()
    {
        Application.EnableVisualStyles();
        using (OpenFileDialog dialog = new OpenFileDialog())
        {
            dialog.Title = "选择 360° 全景图片";
            dialog.Filter = "全景图片|*.jpg;*.jpeg;*.png;*.webp;*.gif|所有文件|*.*";
            return dialog.ShowDialog() == DialogResult.OK ? dialog.FileName : null;
        }
    }

    private static string GetMime(string extension)
    {
        switch (extension.ToLowerInvariant())
        {
            case ".png": return "image/png";
            case ".webp": return "image/webp";
            case ".gif": return "image/gif";
            case ".jpg":
            case ".jpeg": return "image/jpeg";
            default: throw new NotSupportedException("不支持的图片格式：" + extension);
        }
    }

    private static string ReadTemplate()
    {
        const string encoded = "__TEMPLATE_BASE64__";
        return Encoding.UTF8.GetString(Convert.FromBase64String(encoded));
    }
}
