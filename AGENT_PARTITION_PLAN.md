# AGENT_PARTITION_PLAN.md

更新时间：2026-03-27

## 目标
在同一 GitHub 仓库内，按角色分区管理 ZeroOne Venture 投研交易系统，兼顾：
- 共享基础设施统一维护
- 角色沉淀边界清晰
- 未来可低成本拆分为独立仓库

## 当前采用方案
同仓库分区，不分仓库。

## 目录结构

```text
shared/
  rules/
  workflows/
  templates/
  modules/
  memory/

agents/
  longhaochen/
    memory/
    workflows/
    templates/
    rules/
    reports/

  wanglin/
    memory/
    workflows/
    templates/
    rules/
    reports/
```

## 角色定位
### 龙皓晨
- 投研交易组组长
- 总调度 / 总裁决 / 主报告输出者
- 负责跨市场判断、主线识别、总协调与总复盘

### 王林
- 投研交易组加密交易执行员
- 负责加密市场执行沉淀、执行复盘、执行日志与加密交易规则迭代

### shared
- 共用规则
- 共用 workflows
- 共用 templates
- 共用 modules
- 共用公共记忆与系统基础设施

## 放置原则
### 放到 shared/
适用于：
- 两个角色都要用的内容
- 系统级规则与公共工作流
- 公共模板、模块、共享机制

### 放到 agents/longhaochen/
适用于：
- 组长视角的长期记忆
- 总调度规则
- 跨市场主报告沉淀
- 总复盘与总裁决记录

### 放到 agents/wanglin/
适用于：
- 加密执行日志
- 执行策略与执行规则
- 加密交易复盘
- 只属于王林执行线的模板与报告

## 迁移原则
当前先建分区骨架，不强制立即搬迁现有文件。
后续按“新增内容优先进入正确分区、旧内容逐步迁移”的方式平滑过渡。

## 未来拆仓原则
如果未来王林从“执行员”演化为独立系统，可直接将 `agents/wanglin/` 目录迁出为独立仓库。
当前结构已为未来低成本拆仓预留边界。
