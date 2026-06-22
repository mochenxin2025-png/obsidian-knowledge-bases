# Category Mapping for Obsidian Vault

Maps tags and keywords to vault subdirectories. Used by Stage 3 to place generated notes in the correct folder.

## Mapping Table

| Tag / Keyword | → Directory |
|---------------|-------------|
| 理财, 定投, 复利, 基金, 资产配置, 经济学, 财商, 指数, ETF, 被动收入, 止盈 | `理财认知/` |
| agent, ai, 大模型, 记忆, 架构, LLM, skill, hermes, 自动化, 浏览器 | `AI-Agent/` |
| 心理学, 弗洛伊德, 荣格, 阿德勒, 人格, 情绪, 两性, 受害者, 原生家庭 | `心理学/` |
| 认知, 思维, 习惯, 自我提升, 成长, 阅读, 好书, 常识, 高效能 | `认知提升/` |
| 剪辑, 剪映, PR, 视频制作, 后期 | `剪辑教程/` |
| 抖音, 推流, 自媒体, 运营, 流量, 算法 | `自媒体运营/` |
| 职场, 社交, 贵人, 面试, 工作, 管理, 沟通 | `职场进阶/` |
| 科普, 冷知识, 健康 | `科普知识/` |
| 穿搭, 审美, 形象, 服装, 风格 | `穿搭审美/` |
| 护肤, 皮肤, 成分, 化妆品, 美容, 美白, 防晒 | `护肤知识/` |

## Resolution Order

1. Check tag matches → use first matching directory
2. If no tag matches, scan content keywords
3. If still no match, place in vault root with a note to categorize later

## Naming Convention

```
{核心主题}-{关键描述}.md
```

Examples:
- `复利三要素-本金利率时间.md`
- `Agent记忆机制-三层架构.md`
- `15个护肤真相-行业老兵的避坑指南.md`
