## Baas所有action类型和属性

### 主要类型`t`
> type action类型 分为一下几种
- round 回合
- click 点击事件
  - p 是 `position` 点击的位置区域
- exchange 点击左下角切换部队
- move 移动
- not-move 不移动
- end-turn 结束回合
- get-box 获取宝石箱子

### 通用属性
- desc 行动描述
- ec 行动结束后，等待左下角换队
- wait-over 强制等待行动结束（这种情况一般不会自动换队，或有较长动画过渡）
- before 前置等待时间(秒)
- after 后置等待时间(秒)