$ni_path = "HKLM:\SOFTWARE\Native Instruments"
$keys = Get-ChildItem -Path $ni_path
foreach ($key in $keys) {
    $v = Get-ItemProperty -Path $key.PSPath -Name "Visibility" -ErrorAction SilentlyContinue
    if ($null -ne $v) {
        if ($v.Visibility -ne 3) {
            Write-Host "Library: $($key.PSChildName), Visibility: $($v.Visibility)"
        }
    }
}
