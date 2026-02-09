$ni_path = "HKCU:\Software\Native Instruments"
$keys = Get-ChildItem -Path $ni_path
foreach ($key in $keys) {
    if (Get-ItemProperty -Path $key.PSPath -Name "UserRemoved" -ErrorAction SilentlyContinue) {
        $val = Get-ItemProperty -Path $key.PSPath -Name "UserRemoved"
        $idx = Get-ItemProperty -Path $key.PSPath -Name "UserListIndex" -ErrorAction SilentlyContinue
        Write-Host "Library: $($key.PSChildName), UserRemoved: $($val.UserRemoved), UserListIndex: $($idx.UserListIndex)"
    }
}
