# frp 内网穿透

## 功能

通过 frp 将 Windows 电脑的 SSH 端口（22）暴露到公网服务器，实现内网穿透。

## 系统要求

- **客户端（Windows）**：PowerShell 管理员权限
- **服务端（Linux）**：需要公网 IP 的 Linux 服务器

## 一、服务端部署（服务器管理员）

### 1. 下载 frp

```bash
# 下载 frp
wget https://github.com/fatedier/frp/releases/download/v0.51.3/frp_0.51.3_linux_amd64.tar.gz
tar -xzf frp_0.51.3_linux_amd64.tar.gz
cd frp_0.51.3_linux_amd64
```

### 2. 配置 frps

创建 `/etc/frp/frps.ini`:

```ini
[common]
bind_port = 7000
token = 你的Token

# SSH 穿透端口
[ssh]
listen_port = 6000
```

### 3. 启动 frps

```bash
./frps -c /etc/frp/frps.ini
```

### 4. 开放防火墙端口

```bash
firewall-cmd --add-port=7000/tcp --permanent
firewall-cmd --add-port=6000/tcp --permanent
firewall-cmd --reload
```

---

## 二、客户端部署（Windows 用户）

### 1. 下载脚本

从 GitHub 下载 `frp_client_setup.ps1`

或者直接用 PowerShell 下载：

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/1797552175/openclawScripts/main/frp_client_setup.ps1" -OutFile frp_client_setup.ps1
```

### 2. 以管理员身份运行 PowerShell

右键点击 PowerShell -> "以管理员身份运行"

### 3. 运行安装脚本

```powershell
# Token 联系管理员获取
.\frp_client_setup.ps1 -Token '你的Token'
```

### 4. 启动 frpc

安装完成后，运行 `C:\frp\start.bat` 启动客户端

---

## 三、连接测试

客户端 frpc 连接成功后，在服务端 SSH 到客户端：

```bash
ssh 用户名@服务器IP -p 6000
```

---

## 多设备支持

可以为不同设备分配不同端口：

```powershell
# 设备 A
.\frp_client_setup.ps1 -Token 'Token' -RemotePort 6000

# 设备 B
.\frp_client_setup.ps1 -Token 'Token' -RemotePort 6001
```

---

## 常用命令

### 客户端 - 启动 frpc
```powershell
C:\frp\frpc.exe -c C:\frp\frpc.ini
```

### 客户端 - 停止 frpc
按 `Ctrl+C`

### 客户端 - 卸载
删除 `C:\frp` 文件夹

---

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| ServerAddr | 150.109.243.164 | frp 服务器地址 |
| ServerPort | 7000 | frp 服务器端口 |
| Token | (必填) | 认证 Token |
| RemotePort | 6000 | 映射到服务器的端口 |
