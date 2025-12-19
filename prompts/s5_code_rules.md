# S5 阶段代码强约束规则

## 1. 记忆重载 (Context Refresh)
每项子任务开始前必须声明：
[Context Refresh]
- Sub-task ID: 
- Layer: 
- Forbidden Constraints: 

## 2. 变更熔断 (Change Fuse)
发现架构不足以支撑实现时，必须停止并请求回滚 S3，禁止 Dirty Hack。

## 3. 伪 TDD
写代码前必须在注释中声明正确性断言。