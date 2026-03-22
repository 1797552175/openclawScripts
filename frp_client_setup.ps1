# frp 内网穿透客户端安装脚本
# 使用方法：以管理员身份运行 PowerShell，然后运行此脚本

param(
    [string]$ServerAddr = "150.109.243.164",
    [int]$ServerPort = 7000,
    [string]$Token = "",
    [int]$RemotePort = 6000
)

$ErrorActionPreference = "Stop"

# 检查是否为管理员
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "错误：请以管理员身份运行此脚本！" -ForegroundColor Red
    Write-Host "右键点击 PowerShell，选择 '以管理员身份运行'" -ForegroundColor Yellow
    exit 1
}

# 检查 Token 是否提供
if ([string]::IsNullOrWhiteSpace($Token)) {
    Write-Host "错误：Token 不能为空！" -ForegroundColor Red
    Write-Host "请向管理员获取 Token，然后运行：" -ForegroundColor Yellow
    Write-Host "  .\frp_client_setup.ps1 -Token '你的Token'" -ForegroundColor Cyan
    exit 1
}

$FRP_VERSION = "0.51.3"
$FRP_URL = "https://github.com/fatedier/frp/releases/download/v${FRP_VERSION}/frp_${FRP_VERSION}_windows_amd64.zip"
$INSTALL_DIR = "C:\frp"
$ZIP_FILE = "$env:TEMP\frp.zip"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  frp 内网穿透客户端安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "服务器: $ServerAddr" -ForegroundColor White
Write-Host "远程端口: $RemotePort" -ForegroundColor White
Write-Host ""

# 1. 创建安装目录
Write-Host "[1/5] 创建安装目录..." -ForegroundColor Yellow
if (Test-Path $INSTALL_DIR) {
    Write-Host "  目录已存在，跳过" -ForegroundColor Gray
} else {
    New-Item -ItemType Directory -Path $INSTALL_DIR -Force | Out-Null
    Write-Host "  创建完成" -ForegroundColor Green
}

# 2. 下载 frp
Write-Host "[2/5] 下载 frp v$FRP_VERSION..." -ForegroundColor Yellow
if (Test-Path $ZIP_FILE) {
    Remove-Item $ZIP_FILE -Force
}

try {
    Write-Host "  下载地址: $FRP_URL" -ForegroundColor Gray
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $FRP_URL -OutFile $ZIP_FILE -UseBasicParsing
    Write-Host "  下载完成" -ForegroundColor Green
} catch {
    Write-Host "  下载失败: $_" -ForegroundColor Red
    exit 1
}

# 3. 解压
Write-Host "[3/5] 解压文件..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $ZIP_FILE -DestinationPath $INSTALL_DIR -Force
    # 重命名文件夹为 frp（如果需要）
    $extractedDir = Join-Path $INSTALL_DIR "frp_${FRP_VERSION}_windows_amd64"
    if ((Test-Path $extractedDir) -and ($extractedDir -ne $INSTALL_DIR)) {
        Get-ChildItem $extractedDir | Move-Item -Destination $INSTALL_DIR -Force
        Remove-Item $extractedDir -Force
    }
    Write-Host "  解压完成" -ForegroundColor Green
} catch {
    Write-Host "  解压失败: $_" -ForegroundColor Red
    exit 1
}

# 4. 创建配置文件
Write-Host "[4/5] 创建配置文件..." -ForegroundColor Yellow
$frpcIni = @"
[common]
server_addr = $ServerAddr
server_port = $ServerPort
token = $Token

[ssh]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = $RemotePort
"@

$frpcIniPath = Join-Path $INSTALL_DIR "frpc.ini"
$frpcIni | Set-Content -Path $frpcIniPath -Encoding UTF8
Write-Host "  配置文件: $frpcIniPath" -ForegroundColor Gray
Write-Host "  创建完成" -ForegroundColor Green

# 5. 创建启动脚本
Write-Host "[5/5] 创建启动脚本..." -ForegroundColor Yellow
$startScript = @"
@echo off
title frp 内网穿透客户端
cd /d C:\frp
frpc.exe -c frpc.ini
pause
"@

$startScriptPath = Join-Path $INSTALL_DIR "start.bat"
$startScript | Set-Content -Path $startScriptPath -Encoding ASCII
Write-Host "  启动脚本: $startScriptPath" -ForegroundColor Gray
Write-Host "  创建完成" -ForegroundColor Green

# 清理
Remove-Item $ZIP_FILE -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  安装完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "  1. 双击运行 C:\frp\start.bat 启动 frpc" -ForegroundColor White
Write-Host "  2. 连接成功后告诉我" -ForegroundColor White
Write-Host ""
Write-Host "frpc 将会把本机的 SSH(22端口) 映射到服务器 $ServerAddr 的端口 $RemotePort" -ForegroundColor Gray
Write-Host ""

# 询问是否立即启动
$response = Read-Host "是否立即启动 frpc? (Y/N)"
if ($response -eq "Y" -or $response -eq "y") {
    Write-Host ""
    Write-Host "正在启动 frpc..." -ForegroundColor Cyan
    Write-Host "按 Ctrl+C 停止" -ForegroundColor Gray
    Write-Host ""
    $frpcExe = Join-Path $INSTALL_DIR "frpc.exe"
    & $frpcExe -c $frpcIniPath
}
