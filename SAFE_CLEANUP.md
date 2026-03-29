# Git大文件清理指南

## 当前状态

- **Git仓库大小**: ~2.0GB
- **问题原因**: 两个core dump文件（各~15GB）被意外提交到git历史中
- **文件位置**:
  - `core.26562` (15.7GB)
  - `core.74069` (15.7GB)

## 问题分析

1. **提交历史**:
   - `ebe3a97` - 添加了公式识别功能，但意外包含了core文件
   - `3435576` - 尝试移除core文件（文件大小变为0，但仍在历史中）

2. **当前状态**:
   - Core文件已从工作目录删除
   - Core文件已在.gitignore中
   - 但core文件仍在git历史中，占用空间

## 解决方案

### 方案1: 使用git-filter-branch清理（推荐，但需要谨慎）

**优点**: 彻底从历史中移除大文件
**缺点**: 重写历史，需要强制push

**步骤**:

```bash
# 1. 备份当前仓库（重要！）
git clone --bare /workspace /workspace_backup

# 2. 执行清理
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch core.26562 core.74069' \
  --prune-empty --tag-name-filter cat -- --all

# 3. 清理引用
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. 检查清理效果
echo "清理后大小:"
du -sh .git

# 5. 强制推送到远程（⚠️ 慎用！）
# git push origin develop --force
```

### 方案2: 重新组织提交（更安全）

**优点**: 不重写历史，保留所有提交
**缺点**: 大文件仍在历史中，但可以继续使用

**步骤**:

```bash
# 1. 重置到没有大文件的提交
git reset --soft 504a030

# 2. 删除core文件（如果还在）
git rm -f --cached core.26562 core.74069

# 3. 重新提交所有更改
git commit -m "Add formula recognition features"

# 4. 正常push
git push origin develop
```

### 方案3: 使用BFG Repo-Cleaner（最快）

**优点**: 专业工具，清理速度快
**缺点**: 需要安装额外工具

**步骤**:

```bash
# 1. 安装BFG
# 从官网下载: https://rtyley.github.io/bfg-repo-cleaner/

# 2. 运行BFG清理
bfg --delete-files core.26562 core.74069

# 3. 清理引用
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. 强制push
# git push origin develop --force
```

## 推荐方案

### 如果是个人项目，没有 collaborators
**使用方案1** - 彻底清理，节省空间

### 如果是团队项目，需要保留历史
**使用方案2** - 重新组织提交，避免重写历史

### 如果只是想快速清理，可以接受安装新工具
**使用方案3** - 使用BFG，最快最干净

## 重要提醒

⚠️ **无论使用哪种方案，都需要注意**:

1. **先备份！** 一定要备份当前仓库
2. **通知团队** 如果是团队项目，要通知所有成员
3. **测试本地** 先在本地测试，确认没有问题再push
4. **强制push** 如果重写历史，需要使用 `--force` 选项
5. **更新团队成员** 团队成员需要重新clone或reset

## 预防措施

1. **更新.gitignore** - 已添加core文件忽略规则
2. **pre-commit hook** - 添加pre-commit hook检查大文件
3. **定期检查** - 定期检查仓库大小

## 当前建议

**不要立即push！** 建议先执行以下步骤:

1. 备份仓库
2. 检查准备push的内容
3. 确认没有其他大文件
4. 选择合适的清理方案执行
5. 清理完成后再push

---

**状态**: ⏸️ 暂停push，等待用户确认清理方案
