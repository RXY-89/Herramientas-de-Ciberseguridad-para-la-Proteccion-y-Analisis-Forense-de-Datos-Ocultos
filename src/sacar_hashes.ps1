param(
    [string]$ruta,
    [bool]$guardar=$false,
    [string]$carpeta
)

if ( -not $ruta){
    Write-Error "No se proporcionó el parametro 'ruta'" -Category InvalidArgument
    exit 1
}elseif ( -not (Test-Path $ruta)){
    Write-Error "El parametro 'ruta' no es una ruta valida" -Category ObjectNotFound
    exit 1
}
if ($guardar){
    if ( -not $carpeta){
        Write-Error "No se proporcionó el parametro 'carpeta'" -Category InvalidArgument
        exit 1
    } elseif ( -not (Test-Path $carpeta -PathType Container)){
        Write-Error "El parametro 'carpeta' no es un directorio válido" -Category ObjectNotFound
        exit 1
    }
}

if (Test-Path $ruta -PathType Leaf) {
    $hash=Get-FileHash -Path $ruta
    if ($guardar){
        $archivo="$carpeta\lista_hashes.json"
        if ( -not (Test-Path "$archivo")) {@{} | ConvertTo-Json | Set-Content -Path "$archivo"}
        $json=Get-Content $archivo | ConvertFrom-Json
        try{$json.$ruta="$($hash.Hash)"}
        catch{$json | Add-Member -NotePropertyName "$ruta" -NotePropertyValue "$($hash.Hash)"}
        $json | ConvertTo-Json | Set-Content -Path $archivo
    }else{
        Write-Output $hash.Hash
    }
} else{
    $hashes = @{}
    Get-ChildItem -Path $ruta -File | ForEach-Object {
        $hash=Get-FileHash -Path $_.FullName
        $hashes["$($_.name)"]="$($hash.Hash)"
    }
    if ($guardar){
        $nombre = Split-Path $ruta -Leaf
        $hashes | ConvertTo-Json | Set-Content -Path "$carpeta\hashes_$nombre.json"
    }else{
        $hashes | ConvertTo-Json -Compress
    }
    
}