# 简单的功能测试脚本
print("=== 文字转图片工具测试 ===")
print("正在导入模块...")

try:
    # 尝试导入模块
    from text_to_image import create_text_image
    print("✅ 模块导入成功")
    
    # 检查PIL是否可用
    try:
        from PIL import Image
        print("✅ Pillow库可用")
        
        # 测试基本功能（使用默认字体）
        print("\n开始测试核心功能...")
        try:
            # 创建一个简单的测试图片
            width, height = create_text_image(
                text="测试文本",
                font_path="",  # 空路径将使用默认字体
                output_path="test_output.png",
                font_size=20,
                text_color=(0, 0, 0),
                bg_color=(255, 255, 255),
                width=400,
                height=300,
                horizontal_align="center",
                vertical_align="center",
                padding=20
            )
            print(f"✅ 测试成功！创建了 {width}x{height} 的图片")
            print(f"✅ 图片已保存至: test_output.png")
        except Exception as e:
            print(f"❌ 功能测试失败: {str(e)}")
            print("   可能的原因: 字体问题、权限问题或其他运行时错误")
            
    except ImportError:
        print("❌ Pillow库不可用")
        print("   请先安装依赖: 'python -m pip install pillow'")
        
    except Exception as e:
        print(f"❌ 导入测试失败: {str(e)}")
        
finally:
    print("\n=== 测试完成 ===")
    print("\n代码结构已经重构完成，主要改进:")
    print("1. 消除了代码冗余 - GUI现在直接调用核心模块")
    print("2. 代码模块化 - 函数职责单一，结构更清晰")
    print("3. 改进了错误处理和资源管理")
    print("\n请确保安装所有依赖后再运行完整功能")