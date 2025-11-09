param(
    [Parameter(Mandatory=$true)][string]$ruta,
    [ValidateSet("True","False")]$guardar="False",
    [string]$archivo
)


if ( -not (Test-Path $ruta)){
    Write-Error "El parametro 'ruta' no es una ruta valida" -Category InvalidArgument
    exit 1
}
if ($guardar -eq "True"){
    if ( -not $archivo){
        Write-Error "No se proporcionó el parametro 'archivo'" -Category ObjectNotFound
        exit 1
    } elseif ( -not (Test-Path (Split-Path $archivo))){
        Write-Error "El parametro 'archivo' no tiene su carpeta padre" -Category InvalidArgument
        exit 1
    }
}

if (Test-Path $ruta -PathType Leaf) {
    $hash=Get-FileHash -Path $ruta
    if ($guardar -eq "True"){
        if ( -not (Test-Path "$archivo")) {@{} | ConvertTo-Json | Set-Content -Path "$archivo"}
        $json=Get-Content $archivo | ConvertFrom-Json
        try{$json.$ruta="$($hash.Hash)"}
        catch{$json | Add-Member -NotePropertyName "$ruta" -NotePropertyValue "$($hash.Hash)"}
        $json | ConvertTo-Json | Set-Content -Path $archivo
    } else{
        Write-Output $hash.Hash
    }
} else{
    $hashes = @{}
    Get-ChildItem -Path $ruta -File | ForEach-Object {
        $hash=Get-FileHash -Path $_.FullName
        $hashes["$($_.name)"]="$($hash.Hash)"
    }
    if ($guardar -eq "True"){
        $hashes | ConvertTo-Json | Set-Content -Path "$archivo"
    }else{
        $hashes | ConvertTo-Json -Compress
    }
}
