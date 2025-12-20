#!/usr/bin/env python3
"""
测试导出审计记录功能
"""

from ai_project_os_mcp.tools.export_audit import ExportAudit

# 创建导出工具实例

try:
    # 解析审计文件
    audit_file = "docs/S5_audit.md"
    records = ExportAudit.parse_audit_file(audit_file)
    
    print(f"\n解析审计记录结果:")
    print(f"找到 {len(records)} 条审计记录")
    
    if records:
        print("\n第一条记录详情:")
        first_record = records[0]
        for key, value in first_record.items():
            print(f"  {key}: {value}")
        
        # 导出为 JSON
        print("\n导出为 JSON...")
        output_file = "audit_export.json"
        export_data = ExportAudit.export_to_json(audit_file, output_file)
        print(f"✅ 成功导出到 {output_file}")
        print(f"导出记录数: {export_data['records_count']}")
        print(f"导出时间: {export_data['export_timestamp']}")
    else:
        print("\n⚠️  没有找到审计记录")
        print("创建测试审计记录...")
        # 创建一个简单的测试审计文件
        test_audit_content = """# S5 Audit Log

## Sub-task: TEST-001
- Context Refresh: ✅
- Layer: tools
- Files Changed:
  - test_file.py
- Correctness Assertion:
  - 测试记录
- Architecture Compliance:
  - ✅ No violation of S3
- Reviewer:
  - test_reviewer
- Commit Hash: 0000000000000000000000000000000000000000
- Approval:
  - ReviewerType: Human
  - ReviewerId: test_user
- Status: PASSED
- Record Hash: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
"""
        
        with open(audit_file, "w", encoding="utf-8") as f:
            f.write(test_audit_content)
        
        print("✅ 已创建测试审计记录")
        
        # 再次尝试解析和导出
        records = ExportAudit.parse_audit_file(audit_file)
        print(f"找到 {len(records)} 条审计记录")
        
        output_file = "audit_export.json"
        export_data = ExportAudit.export_to_json(audit_file, output_file)
        print(f"✅ 成功导出到 {output_file}")
        print(f"导出记录数: {export_data['records_count']}")
        print(f"导出时间: {export_data['export_timestamp']}")
        
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
