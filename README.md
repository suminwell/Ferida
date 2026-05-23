# Ferida

跟随 [FRIDA](https://github.com/frida/frida) 上游自动修补程序，并为 Android 构建反检测版本的 frida-server 和 frida-gadget。

**提示：不要 fork 此仓库**

## 功能特性

### 反检测补丁
- ✅ 重命名 frida 相关字符串和符号
- ✅ 隐藏 frida 线程和端口
- ✅ 绕过常见检测方法
- ✅ 随机化内存特征

### 在线 JS 加载（新功能！）
- ✅ 从远程 URL 加载 JS 脚本
- ✅ AES-256-GCM 加密支持
- ✅ 动态密钥获取（不嵌入 SO）
- ✅ 多种配置方式
- ✅ 优雅降级到本地配置

## 下载

[最新版本](https://github.com/Ylarod/Florida/releases/latest)

## 快速开始

### 1. 基础用法（本地配置）

在 `libfrida-gadget.so` 旁边放置 `frida-gadget.config`：

```json
{
  "interaction": {
    "type": "script",
    "path": "/data/local/tmp/hook.js"
  }
}
```

### 2. 在线 JS 加载

#### 方式 A：环境变量

```java
public class MainActivity extends Activity {
    static {
    try {
          Class<?> processEnvironment = Class.forName("java.lang.ProcessEnvironment");
      Field theEnvironmentField = processEnvironment.getDeclaredField("theEnvironment");
            theEnvironmentField.setAccessible(true);
            Map<String, String> env = (Map<String, String>) theEnvironmentField.get(null);
            
            // 设置 URL
            env.put("FERIDA_SCRIPT_URL", "https://example.com/hook.json");
            
         // 设置加密密钥（可选）
            env.put("FERIDA_SCRIPT_KEY", "a1b2c3d4e5f6789012345678901234567890123456789012345678901234");
            
        } catch (Exception e) {
        e.printStackTrace();
        }
        
    System.loadLibrary("frida-gadget");
    }
}
```

#### 方式 B：配置文件

在 `libfrida-gadget.so` 旁边创建 `libfrida-gadget.conf`：

```ini
# 在线 JS 配置
FERIDA_SCRIPT_URL=https://example.com/hook.json
FERIDA_SCRIPT_KEY=a1b2c3d4e5f6789012345678901234567890123456789012345678901234
```

**文件命名规则**：
- `libfrida-gadget.so` → `libfrida-gadget.conf`
- `libcc.so` → `libcc.conf`
- `libhook.so` → `libhook.conf`

### 3. 加密 JS 脚本

```bash
cd tools

# 安装依赖
pip install -r requirements.txt

# 生成加密密钥
python3 encrypt_tool.py genkey

# 加密 JS 文件
python3 encrypt_tool.py encrypt hook.js hook.json <密钥>

# 解密验证
python3 encrypt_tool.py decrypt hook.json test.js <密钥>

# 部署到服务器
scp hook.json user@server:/var/www/html/
```

**输出格式**：
```json
{
  "data": "base64_加密的_js_数据"
}
```

## 配置说明
### 配置优先级

#### URL 来源
1. 环境变量 `FERIDA_SCRIPT_URL`
2. 配置文件 `libfrida-gadget.conf` 中的 `FERIDA_SCRIPT_URL`
3. 回退到 `frida-gadget.config`

#### 加密密钥来源
1. JSON 中的 `key` 字段（如果有）
2. 环境变量 `FERIDA_SCRIPT_KEY`
3. 配置文件 `libfrida-gadget.conf` 中的 `FERIDA_SCRIPT_KEY`
4. 无密钥（当作明文）

### 配置文件格式

```ini
# 注释行以 # 开头
# 空行会被忽略

# JS 脚本下载 URL（可选）
FERIDA_SCRIPT_URL=https://example.com/hook.json
# 加密密钥（可选）
FERIDA_SCRIPT_KEY=a1b2c3d4e5f6789012345678901234567890123456789012345678901234
```

**配置文件位置**：
```
/data/app/com.example.app/lib/arm64/
├── libfrida-gadget.so
└── libfrida-gadget.conf
```

## 支持的格式

### 1. 加密 JSON（推荐）
```json
{
  "data": "SGVsbG8gV29ybGQh..."
}
```

### 2. 带密钥的加密 JSON
```json
{
  "key": "a1b2c3d4...",
  "data": "SGVsbG8gV29ybGQh..."
}
```

### 3. 明文 JS
```javascript
console.log("Hello from Frida!");
```

### 4. 明文 JSON
```json
{
  "data": "console.log('Hello');"
}
```

所有格式都支持自动检测和优雅降级。

## 使用场景

### 场景 1: 只用环境变量
```java
env.put("FERIDA_SCRIPT_URL", "https://example.com/hook.json");
env.put("FERIDA_SCRIPT_KEY", "a1b2c3d4...");
System.loadLibrary("frida-gadget");
```
不需要配置文件。

### 场景 2: 只用配置文件
创建 `libfrida-gadget.conf`:
```ini
FERIDA_SCRIPT_URL=https://example.com/hook.json
FERIDA_SCRIPT_KEY=a1b2c3d4...
```
不需要设置环境变量。

### 场景 3: 混合使用
```java
// URL 从环境变量
env.put("FERIDA_SCRIPT_URL", "https://example.com/hook.json");
System.loadLibrary("frida-gadget");
```

配置文件 `libfrida-gadget.conf`:
```ini
# 密钥从配置文件
FERIDA_SCRIPT_KEY=a1b2c3d4...
```

### 场景 4: 只配置 URL，不加密
配置文件 `libfrida-gadget.conf`:
```ini
FERIDA_SCRIPT_URL=https://example.com/hook.js
# 不设置 FERIDA_SCRIPT_KEY，服务器返回明文 JS
```

### 场景 5: 动态控制
```java
// 根据设备 ID 决定是否使用在线 JS
String deviceId = getDeviceId();
if (shouldUseOnlineJS(deviceId)) {
    env.put("FERIDA_SCRIPT_URL", "https://example.com/hook.json");
    env.put("FERIDA_SCRIPT_KEY", fetchKeyFromServer(deviceId));
}
System.loadLibrary("frida-gadget");
```

## 安全特性

- ✅ **动态密钥获取**：加密密钥不嵌入 SO
- ✅ **AES-256-GCM**：256 位密钥的认证加密
- ✅ **随机 IV**：每次加密使用不同的 IV
- ✅ **密钥轮换**：无需重新编译即可轮换密钥
- ✅ **设备特定密钥**：支持每个设备使用不同的加密密钥
- ✅ **优雅降级**：解密失败时回退到明文

## 错误处理

Gadget **永远不会**因为在线 JS 加载而崩溃：

- ❌ 网络错误 → 回退到本地配置
- ❌ 无效 URL → 回退到本地配置
- ❌ 解密失败 → 当作明文处理
- ❌ 无效 JSON → 当作明文处理
- ❌ 缺少配置 → 回退到本地配置

## 工具说明

### encrypt_tool.py

使用 AES-256-GCM 加密/解密 JS 文件：

```bash
# 生成密钥（64 个十六进制字符）
python3 encrypt_tool.py genkey

# 加密 JS 文件
python3 encrypt_tool.py encrypt input.js output.json <key_hex>

# 解密验证
python3 encrypt_tool.py decrypt input.json output.js <key_hex>
```

**依赖安装**：
```bash
pip install -r tools/requirements.txt
```

## 完整示例

### 示例 1: 加密的在线 JS

**1. 生成密钥**
```bash
$ python3 encrypt_tool.py genkey
Generated AES-256 key:
a1b2c3d4e5f678901234567890123456789012345678901234
```

**2. 加密 JS**
```bash
$ python3 encrypt_tool.py encrypt hook.js hook.json a1b2c3d4...
Encrypted: 1234 -> 1262 bytes
Output: hook.json
```

**3. 部署**
```bash
$ scp hook.json user@server:/var/www/html/
```

**4. 配置 Gadget**

`libfrida-gadget.conf`:
```ini
FERIDA_SCRIPT_URL=https://cdn.example.com/hook.json
FERIDA_SCRIPT_KEY=a1b2c3d4e5f6789012345678901234567890123456789012345678901234
```

### 示例 2: 明文在线 JS

**配置文件**：
```ini
FERIDA_SCRIPT_URL=https://cdn.example.com/hook.js
```

**服务器直接返回 JS**：
```javascript
console.log("Hello from online JS!");
```

## 从源码构建

```bash
# 克隆仓库
git clone https://github.com/Ylarod/Florida.git
cd Florida

# 构建
# (GitHub Actions 会在 push 时自动构建)
```

## 注意事项

1. **文件权限**：确保配置文件可读
2. **密钥安全**：如果配置文件包含密钥，注意文件权限
3. **灵活性**：可以只配置 URL，不配置密钥
4. **向后兼容**：如果不使用在线 JS，完全不需要配置文件

## 参考

- [https://github.com/hluwa/Patchs](https://github.com/hluwa/Patchs)
- [https://github.com/feicong/strong-frida](https://github.com/feicong/strong-frida)
- [https://github.com/qtfreet00/AntiFrida](https://github.com/qtfreet00/AntiFrida)
- [https://t.zsxq.com/miIunQN](https://t.zsxq.com/miIunQN)
- [https://github.com/darvincisec/DetectFrida](https://github.com/darvincisec/DetectFrida)
- [https://github.com/b-mueller/frida-detection-demo](https://github.com/b-mueller/frida-detection-demo)

## 致谢

- [@hluwa](https://github.com/hluwa)
- [@feicong](https://github.com/feicong)
- [@r0ysue](https://github.com/r0ysue)
- [@hellodword](https://github.com/hellodword)
- [@qtfreet00](https://github.com/qtfreet00)

## 许可证

与 [Frida](https://github.com/frida/frida) 相同
