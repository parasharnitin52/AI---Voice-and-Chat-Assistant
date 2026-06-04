$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$cacheDirs = @(".next", ".next-local")

foreach ($dir in $cacheDirs) {
    $path = Join-Path $projectRoot $dir
    if (Test-Path -LiteralPath $path) {
        Remove-Item -LiteralPath $path -Recurse -Force
    }
}
