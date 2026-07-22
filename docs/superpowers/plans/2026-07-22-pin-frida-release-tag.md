# Ferida 固定 Frida Release Tag 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标：** 确保 Ferida 的每个 Release 都从同版本的 Frida tag 构建，而不是从 Frida 默认分支构建。

**架构：** `check_version` 继续负责取得最新版 Frida tag。Android 构建任务通过 `FRIDA_VERSION` 接收该值，克隆对应 tag，并在应用 patch 前验证 `HEAD` 与 tag commit 一致。

**技术栈：** GitHub Actions、Bash、Git、YAML。

---

### 任务 1：固定并验证 Frida 源码版本

**文件：**
- 修改：`.github/workflows/build.yml` 中的 `build frida for Android` 步骤
- 测试：使用一次性 Ruby 断言检查工作流文本，不新增永久测试文件

- [ ] **步骤 1：运行修改前断言并确认失败**

运行：

```bash
ruby -e '
workflow = File.read(".github/workflows/build.yml")
required = [
  %q{FRIDA_VERSION: ${{ needs.check_version.outputs.FRIDA_VERSION }}},
  %q{git clone --branch "$FRIDA_VERSION" --recurse-submodules https://github.com/frida/frida},
  %q{git rev-parse "refs/tags/${FRIDA_VERSION}^{commit}"}
]
missing = required.reject { |text| workflow.include?(text) }
abort("缺少固定 Frida tag 的工作流配置：#{missing.join(", ")}") unless missing.empty?
'
```

预期：命令退出码非零，并报告缺少上述配置。

- [ ] **步骤 2：实施最小工作流修改**

将构建步骤改为以下结构，已有 patch 循环及后续构建命令保持不变：

```yaml
- name: build frida for Android
  shell: bash
  env:
    FRIDA_VERSION: ${{ needs.check_version.outputs.FRIDA_VERSION }}
  run: |
    git config --global user.name "GitHub Actions"
    git config --global user.email "41898282+github-actions[bot]@users.noreply.github.com"

    export ANDROID_NDK_ROOT=${{ steps.setup-ndk.outputs.ndk-path }}
    echo "ANDROID_NDK_ROOT=$ANDROID_NDK_ROOT"

    git clone --branch "$FRIDA_VERSION" --recurse-submodules https://github.com/frida/frida
    cd frida

    checked_out_commit="$(git rev-parse HEAD)"
    release_commit="$(git rev-parse "refs/tags/${FRIDA_VERSION}^{commit}")"
    if [ "$checked_out_commit" != "$release_commit" ]; then
      echo "Frida checkout mismatch: HEAD=$checked_out_commit, $FRIDA_VERSION=$release_commit"
      exit 1
    fi
```

- [ ] **步骤 3：重新运行断言并确认通过**

运行步骤 1 的同一条 Ruby 命令。

预期：命令退出码为零且无输出。

- [ ] **步骤 4：验证 YAML 可以解析**

运行：

```bash
ruby -e 'require "yaml"; YAML.load_file(".github/workflows/build.yml"); puts "YAML syntax OK"'
```

预期输出：

```text
YAML syntax OK
```

- [ ] **步骤 5：检查差异与仓库状态**

运行：

```bash
git diff --check
git diff -- .github/workflows/build.yml
git status --short
```

预期：`git diff --check` 无输出；工作流差异只包含版本环境变量、按 tag 克隆和 commit 一致性校验。

- [ ] **步骤 6：提交工作流修复**

```bash
git add .github/workflows/build.yml
git commit -m "Pin builds to Frida release tag"
```
