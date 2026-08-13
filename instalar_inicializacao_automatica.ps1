# Cria um atalho do JARVIS na pasta de Inicializacao do Windows,
# para ele abrir sozinho toda vez que voce ligar o PC.
#
# Como usar: clique com o botao direito neste arquivo -> "Executar com PowerShell".
# Se aparecer aviso de politica de execucao, rode antes (uma vez so):
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

$pastaProjeto = $PSScriptRoot
$pythonw = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source
if (-not $pythonw) {
    $pythonw = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
    Write-Host "Aviso: pythonw.exe nao encontrado, usando python.exe (vai abrir uma janela de console junto)."
}

$pastaInicializacao = [Environment]::GetFolderPath("Startup")
$caminhoAtalho = Join-Path $pastaInicializacao "JARVIS.lnk"

$shell = New-Object -ComObject WScript.Shell
$atalho = $shell.CreateShortcut($caminhoAtalho)
$atalho.TargetPath = $pythonw
$atalho.Arguments = '"' + (Join-Path $pastaProjeto "main.py") + '"'
$atalho.WorkingDirectory = $pastaProjeto
$atalho.WindowStyle = 1
$atalho.Description = "JARVIS - assistente pessoal"
$atalho.Save()

Write-Host "Pronto! Atalho criado em: $caminhoAtalho"
Write-Host "O JARVIS vai abrir sozinho no proximo login do Windows."
Write-Host "Para desativar, delete esse atalho da pasta de Inicializacao."
