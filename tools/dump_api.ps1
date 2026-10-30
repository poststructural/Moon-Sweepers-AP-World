param(
    [string]$Assembly = "C:\Steam\steamapps\common\Moon Sweepers\BepInEx\interop\Assembly-CSharp.dll",
    [string]$Cecil = "C:\Steam\steamapps\common\Moon Sweepers\BepInEx\core\Mono.Cecil.dll",
    [string]$Out = "C:\Users\unowi\Documents\APWorldMaker\MoonSweepersAP\research\api_dump.txt"
)
Add-Type -Path $Cecil
$asm = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($Assembly)
$sb = [System.Text.StringBuilder]::new()

function Format-Type($t) {
    if ($null -eq $t) { return "?" }
    return $t.FullName
}

function Dump-Type($type, $indent) {
    $pad = " " * $indent
    $base = if ($type.BaseType) { $type.BaseType.FullName } else { "" }
    [void]$sb.AppendLine("$pad$($type.FullName) : $base")
    foreach ($f in $type.Fields) {
        $mods = @()
        if ($f.IsStatic) { $mods += "static" }
        if ($f.IsLiteral) { $mods += "const" }
        if ($f.IsPublic) { $mods += "public" } elseif ($f.IsPrivate) { $mods += "private" } else { $mods += "internal" }
        [void]$sb.AppendLine("$pad  FIELD [$($mods -join ' ')] $(Format-Type $f.FieldType) $($f.Name)")
    }
    foreach ($p in $type.Properties) {
        $acc = @()
        if ($p.GetMethod) { $acc += "get" }
        if ($p.SetMethod) { $acc += "set" }
        [void]$sb.AppendLine("$pad  PROP $(Format-Type $p.PropertyType) $($p.Name) {$($acc -join ',')}")
    }
    foreach ($e in $type.Events) {
        [void]$sb.AppendLine("$pad  EVENT $(Format-Type $e.EventType) $($e.Name)")
    }
    foreach ($m in $type.Methods) {
        $mods = @()
        if ($m.IsStatic) { $mods += "static" }
        if ($m.IsPublic) { $mods += "public" } elseif ($m.IsPrivate) { $mods += "private" } else { $mods += "internal" }
        if ($m.IsVirtual) { $mods += "virtual" }
        $ps = ($m.Parameters | ForEach-Object { "$(Format-Type $_.ParameterType) $($_.Name)" }) -join ", "
        [void]$sb.AppendLine("$pad  METHOD [$($mods -join ' ')] $(Format-Type $m.ReturnType) $($m.Name)($ps)")
    }
    foreach ($n in $type.NestedTypes) {
        Dump-Type $n ($indent + 2)
    }
}

foreach ($t in $asm.MainModule.Types) {
    Dump-Type $t 0
    [void]$sb.AppendLine("")
}

$sb.ToString() | Set-Content -Path $Out -Encoding utf8
Write-Host "wrote $Out ($((Get-Item $Out).Length) bytes)"
