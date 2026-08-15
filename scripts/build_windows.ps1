param(
    [switch]$Install,
    [switch]$Uninstall
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$distDir = Join-Path $projectRoot 'dist'
$source = Join-Path $PSScriptRoot 'windows\PanoViewer.cs'
$icon = Join-Path $projectRoot 'assets\PanoViewer.ico'
$iconBuilder = Join-Path $PSScriptRoot 'windows\make_icon.py'
$template = Join-Path $distDir 'template.html'
$output = Join-Path $distDir 'PanoViewer.exe'
$generatedSource = Join-Path $distDir 'PanoViewer.generated.cs'
$version = [IO.File]::ReadAllText((Join-Path $projectRoot 'VERSION')).Trim()
$installDir = Join-Path $env:LOCALAPPDATA 'Programs\PanoViewer'
$installedExe = Join-Path $installDir 'PanoViewer.exe'
$installedIcon = Join-Path $installDir 'PanoViewer.ico'
$extensions = '.jpg', '.jpeg', '.png', '.webp', '.gif'

function Invoke-Python {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    $python = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($python) {
        & $python.Source @Arguments
        return
    }
    $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($launcher) {
        & $launcher.Source -3 @Arguments
        return
    }
    throw 'Python 3 was not found. Install Python 3 and add it to PATH.'
}

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

Invoke-Python (Join-Path $PSScriptRoot 'build.py')
if ($LASTEXITCODE -ne 0) { throw 'HTML build failed.' }
if (-not (Test-Path -LiteralPath $icon)) {
    Invoke-Python $iconBuilder
    if ($LASTEXITCODE -ne 0) { throw 'Icon build failed.' }
}

if (Test-Path -LiteralPath $output) { Remove-Item -LiteralPath $output -Force }
$templateBase64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($template))
$sourceText = [IO.File]::ReadAllText($source).Replace('__TEMPLATE_BASE64__', $templateBase64).Replace('__APP_VERSION__', $version)
[IO.File]::WriteAllText($generatedSource, $sourceText, (New-Object Text.UTF8Encoding($true)))
$compiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
if (-not (Test-Path -LiteralPath $compiler)) {
    $compiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\csc.exe'
}
& $compiler /nologo /target:winexe /optimize+ /reference:System.dll `
    /reference:System.Windows.Forms.dll "/win32icon:$icon" "/out:$output" $generatedSource
if ($LASTEXITCODE -ne 0) { throw 'C# compilation failed.' }
Remove-Item -LiteralPath $generatedSource -Force
Write-Host "Built $output"

if ($Install) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    Copy-Item -LiteralPath $output -Destination $installedExe -Force
    Copy-Item -LiteralPath $icon -Destination $installedIcon -Force

    $appKey = 'HKCU:\Software\Classes\Applications\PanoViewer.exe'
    New-Item -Path "$appKey\shell\open\command" -Force | Out-Null
    New-Item -Path "$appKey\DefaultIcon" -Force | Out-Null
    Set-ItemProperty -LiteralPath "$appKey\DefaultIcon" -Name '(default)' -Value $installedIcon
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
    New-Item -Path "$progId\DefaultIcon" -Force | Out-Null
    Set-ItemProperty -LiteralPath $progId -Name '(default)' -Value 'PanoViewer 360 Image'
    Set-ItemProperty -LiteralPath "$progId\DefaultIcon" -Name '(default)' -Value $installedIcon
    Set-ItemProperty -LiteralPath "$progId\shell\open\command" -Name '(default)' -Value "`"$installedExe`" `"%1`""
    Write-Host "Installed $installedExe"
    & (Join-Path $env:WINDIR 'System32\ie4uinit.exe') -show 2>$null
    Write-Host 'PanoViewer is now available under Open with > Choose another app.'
}
