# frp 内网穿透客户端

## 功能

通过 frp 将 Windows 电脑的 SSH 端口（22）暴露到公网服务器，实现内网穿透。

## 使用方法

### 前提条件

- Windows 电脑
- PowerShell（管理员权限）
- 已获取 frp 服务器的 Token（联系管理员获取）

### 安装步骤

1. **下载脚本**

   将 `frp_client_setup.ps1` 下载到 Windows 电脑

2. **以管理员身份运行 PowerShell**

   右键点击 PowerShell -> "以管理员身份运行"

3. **运行安装脚本**

   ```powershell
   .\frp_client_setup.ps1 -Token '你的Token'
   ```

   例如：
   ```powershell
   .\frp_client_setup.ps1 -Token 'mySecretToken123'
   ```

4. **启动 frpc**

   安装完成后，运行 `C:\frp\start.bat` 启动客户端

5. **测试连接**

   连接成功后，通过以下方式 SSH 到你的电脑：
   ```bash
   ssh username@服务器IP -p 6000
   ```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| ServerAddr | 150.109.243.164 | frp 服务器地址 |
| ServerPort | 7000 | frp 服务器端口 |
| Token | (必填) | 认证 Token |
| RemotePort | 6000 | 映射到服务器的端口 |

## 常用命令

### 启动 frpc
```powershell
C:\frp\frpc.exe -c C:\frp\frpc.ini
```

### 停止 frpc
在运行窗口按 `Ctrl+C`

### 卸载
删除 `C:\frp` 文件夹即可

## 注意事项

- Token 请向管理员获取
- 需要保持 frpc 运行才能维持穿透连接
- 建议开机自启动 frpc（可通过任务计划程序设置）
