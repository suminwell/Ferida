# 将 Ferida 构建固定到 Frida Release Tag

## 目标

确保每个 Ferida GitHub Release 都使用其版本号对应的 Frida tag 源码构建，
而不是在工作流运行时直接使用 Frida 默认分支的最新源码。

## 修改范围

只修改 `ferida/.github/workflows/build.yml`。`android-core` 的工作流及其独立的
发布周期保持不变，Ferida 发布成功后不会自动触发 `android-core` 发布。

## 设计方案

Android 构建任务会将 `check_version` 任务检测到的版本设置为
`FRIDA_VERSION` 环境变量。克隆 Frida 时使用
`--branch "$FRIDA_VERSION"` 和 `--recurse-submodules`，从一开始就检出
Release 对应的 Frida 主仓库源码及其锁定的子模块版本。

克隆完成后，工作流会比较当前 `HEAD` 与
`refs/tags/$FRIDA_VERSION` 指向的 commit。tag 不存在或 commit 不一致时，
工作流会在应用任何 Ferida patch 之前立即失败。

现有的 Ferida patch 应用循环和四种 Android ABI 构建流程保持不变。如果新版
Frida 与现有 patch 不兼容，`git am` 应当失败；这种 patch 适配仍由人工完成，
不会尝试自动修改补丁。

## 错误处理

- Frida Release tag 不存在：`git clone --branch` 失败。
- 检出的 commit 与 tag 不一致：显式一致性校验失败。
- Ferida patch 与新版 Frida 冲突：`git am` 失败。
- 上述失败均不会触发 `android-core` 发布。

## 验证方式

本次只修改 GitHub Actions 工作流配置，验证方式如下：

1. 修改前运行 shell 断言；由于克隆命令没有选择 `FRIDA_VERSION`，断言应失败。
2. 修改后再次运行相同断言，确认其通过。
3. 解析修改后的 YAML，确认语法有效。
4. 检查最终 diff，确认没有修改 `android-core` 文件或 Ferida 的其他行为。
