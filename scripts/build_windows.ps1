param(
    [switch]$Install,
    [switch]$Uninstall
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$distDir = Join-Path $projectRoot 'dist'
$source = Join-Path $PSScriptRoot 'windows\PanoViewer.cs'
$template = Join-Path $distDir 'template.html'
$output = Join-Path $distDir 'PanoViewer.exe'
$generatedSource = Join-Path $distDir 'PanoViewer.generated.cs'
$installDir = Join-Path $env:LOCALAPPDATA 'Programs\PanoViewer'
$installedExe = Join-Path $installDir 'PanoViewer.exe'
$extensions = '.jpg', '.jpeg', '.png', '.webp', '.gif'

function Remove-Registration {
    Remove-Item -LiteralPath 'HKCU:\Software\Classes\Applications\PanoViewer.exe' -Recurse -Force -ErrorAction SilentlyContinue
    foreach ($extension in $extensions) {
        Remove-ItemProperty -LiteralPath "HKCU:\Software\Classes\$extension\OpenWithProgids" -Name 'PanoViewer.Image' -ErrorAction SilentlyContinue
    }
    Remove-Item -LiteralPath 'HKCU:\Software\Classes\PanoViewer.Image' -Recurse -Force -ErrorAction SilentlyContinue
}

if ($Uninstall) {
    Remove-Registration
    if (Test-Path -LiteralPath $installDir) {
        Remove-Item -LiteralPath $installDir -Recurse -Force
    }
    Write-Host 'PanoViewer was removed from the current user Open With list.'
    exit 0
}

& py -3 (Join-Path $PSScriptRoot 'build.py')
if ($LASTEXITCODE -ne 0) { throw 'HTML build failed.' }

if (Test-Path -LiteralPath $output) { Remove-Item -LiteralPath $output -Force }
$templateBase64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($template))
$sourceText = [IO.File]::ReadAllText($source).Replace('__TEMPLATE_BASE64__', $templateBase64)
[IO.File]::WriteAllText($generatedSource, $sourceText, (New-Object Text.UTF8Encoding($true)))
Add-Type -Path $generatedSource -ReferencedAssemblies 'System.dll', 'System.Windows.Forms.dll' `
    -OutputAssembly $output -OutputType WindowsApplication
Remove-Item -LiteralPath $generatedSource -Force
Write-Host "Built $output"

if ($Install) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    Copy-Item -LiteralPath $output -Destination $installedExe -Force

    $appKey = 'HKCU:\Software\Classes\Applications\PanoViewer.exe'
    New-Item -Path "$appKey\shell\open\command" -Force | Out-Null
    Set-ItemProperty -LiteralPath "$appKey\shell\open\command" -Name '(default)' -Value "`"$installedExe`" `"%1`""
    New-Item -Path "$appKey\SupportedTypes" -Force | Out-Null
    foreach ($extension in $extensions) {
        New-ItemProperty -LiteralPath "$appKey\SupportedTypes" -Name $extension -Value '' -PropertyType String -Force | Out-Null
        $openWith = "HKCU:\Software\Classes\$extension\OpenWithProgids"
        New-Item -Path $openWith -Force | Out-Null
        New-ItemProperty -LiteralPath $openWith -Name 'PanoViewer.Image' -Value '' -PropertyType String -Force | Out-Null
    }

    $progId = 'HKCU:\Software\Classes\PanoViewer.Image'
    New-Item -Path "$progId\shell\open\command" -Force | Out-Null
    Set-ItemProperty -LiteralPath $progId -Name '(default)' -Value 'PanoViewer 360 Image'
    Set-ItemProperty -LiteralPath "$progId\shell\open\command" -Name '(default)' -Value "`"$installedExe`" `"%1`""
    Write-Host "Installed $installedExe"
    Write-Host 'PanoViewer is now available under Open with > Choose another app.'
}
