param(
    [Parameter(Mandatory=$true)][string]$ruta,
    [ValidateSet("True","False")]$guardar="False",
    [string]$archivo
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

if (-not (Test-Path $ruta)) {
    Write-Error "Ruta inválida"
    exit 1
}

if (Test-Path $ruta -PathType Leaf) {
    $hashObj = Get-FileHash -Path $ruta -Algorithm SHA256
    $hashStr = $hashObj.Hash

    if ($guardar -eq "True") {

        if (-not (Test-Path $archivo)) { "{}" | Set-Content $archivo -Encoding UTF8 }
        
        $json = Get-Content $archivo -Raw -Encoding UTF8 | ConvertFrom-Json

        if ($json -is [PSCustomObject]) {
            $json | Add-Member -MemberType NoteProperty -Name $ruta -Value $hashStr -Force
        } else {
            $json["$ruta"] = $hashStr
        }
        $json | ConvertTo-Json -Depth 2 | Set-Content $archivo -Encoding UTF8
    } else {
        Write-Output $hashStr
    }

} else {
    $hashes = @{}
    Get-ChildItem -Path $ruta -File | ForEach-Object {
        $h = Get-FileHash -Path $_.FullName -Algorithm SHA256
        $hashes["$($_.Name)"] = $h.Hash
    }

    if ($guardar -eq "True") {
        $hashes | ConvertTo-Json | Set-Content $archivo -Encoding UTF8
    } else {
        $hashes | ConvertTo-Json -Compress
    }
}
