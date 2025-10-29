# 简单的Python环境测试脚本
print("=== Python环境测试 ===")
print("Python版本:")
import sys
print(sys.version)
print("\n环境变量PATH的前几个路径:")
paths = sys.path[:5]
for i, path in enumerate(paths):
    print(f"{i+1}: {path}")
print("\n=== 测试完成 ===")