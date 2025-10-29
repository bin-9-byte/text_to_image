# 尝试导入必要的库，提供优雅的错误处理
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("错误: 缺少Pillow库。请运行 'pip install pillow' 安装依赖。")
    print("如果pip命令不可用，请尝试 'python -m pip install pillow'")
    # 这里不抛出异常，让用户看到错误信息

import argparse
import textwrap


def create_text_image(
    text,
    font_path,
    output_path,
    font_size=40,
    text_color=(0, 0, 0),
    bg_color=(255, 255, 255),
    width=None,
    height=None,
    horizontal_align="center",
    vertical_align="center",
    padding=20,
):
    """
    创建带有特定样式的文字图片
    
    参数:
        text: 要渲染的文字
        font_path: 字体文件路径
        output_path: 输出图片路径
        font_size: 字体大小
        text_color: 文字颜色(RGB元组)
        bg_color: 背景颜色(RGB元组)
        width: 图片宽度
        height: 图片高度
        horizontal_align: 水平对齐(left/center/right)
        vertical_align: 垂直对齐(top/center/bottom)
        padding: 文字与图片边缘的间距
    """
    # 加载字体
    font = _load_font(font_path, font_size)
    
    # 创建临时绘图对象计算文本尺寸
    temp_draw = ImageDraw.Draw(Image.new("RGB", (1, 1), bg_color))
    
    # 文本换行处理
    wrapped_text = _wrap_text(text, font, width or 800, padding)
    
    # 计算文本尺寸
    line_dimensions = _calculate_text_dimensions(wrapped_text, font, temp_draw)
    total_text_width = max(dim[0] for dim in line_dimensions) if line_dimensions else 0
    total_text_height = sum(dim[1] for dim in line_dimensions) + \
                       (len(line_dimensions) - 1) * (font_size // 4)
    
    # 确定图片尺寸
    img_width, img_height = width or min(total_text_width + 2 * padding, 800), \
                           height or (total_text_height + 2 * padding)
    
    # 创建图片
    img = Image.new("RGB", (img_width, img_height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # 计算文字起始位置并绘制
    _draw_text(draw, wrapped_text, line_dimensions, font, text_color, 
              img_width, img_height, total_text_height, 
              horizontal_align, vertical_align, padding, font_size)
    
    img.save(output_path)
    print(f"图片已保存至: {output_path}（分辨率：{img_width}x{img_height}）")
    return img_width, img_height


def _load_font(font_path, font_size):
    """加载字体，处理异常情况"""
    try:
        if font_path and len(font_path) > 0:
            return ImageFont.truetype(font_path, font_size)
    except (IOError, OSError):
        print(f"无法加载字体文件: {font_path}")
    return ImageFont.load_default()


def _wrap_text(text, font, max_width, padding):
    """处理文本换行"""
    # 计算平均字符宽度用于换行
    bbox = font.getbbox("x")
    avg_char_width = bbox[2] - bbox[0]
    max_chars_per_line = (max_width - 2 * padding) // avg_char_width
    
    wrapped_text = []
    for paragraph in text.split("\n"):
        wrapped = textwrap.fill(paragraph, width=max_chars_per_line)
        wrapped_text.extend(wrapped.split("\n"))
    
    return wrapped_text


def _calculate_text_dimensions(wrapped_text, font, draw):
    """计算每行文本的宽度和高度"""
    line_dimensions = []
    for line in wrapped_text:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_dimensions.append((bbox[2] - bbox[0], bbox[3] - bbox[1]))
    return line_dimensions


def _draw_text(draw, wrapped_text, line_dimensions, font, text_color,
               img_width, img_height, total_text_height,
               horizontal_align, vertical_align, padding, font_size):
    """绘制文本到图片上"""
    # 计算垂直起始位置
    if vertical_align == "top":
        y_text = padding
    elif vertical_align == "center":
        y_text = (img_height - total_text_height) // 2
    else:  # bottom
        y_text = img_height - padding - total_text_height
    
    # 绘制每行文字
    line_spacing = font_size // 4
    for i, line in enumerate(wrapped_text):
        line_width = line_dimensions[i][0]
        
        # 计算水平起始位置
        if horizontal_align == "left":
            x_text = padding
        elif horizontal_align == "center":
            x_text = (img_width - line_width) // 2
        else:  # right
            x_text = img_width - padding - line_width
        
        draw.text((x_text, y_text), line, font=font, fill=text_color)
        y_text += line_dimensions[i][1] + line_spacing


def main():
    parser = argparse.ArgumentParser(
        description="文字转图片（支持分辨率、对齐方式、颜色控制）"
    )
    # 基础参数
    parser.add_argument(
        "--text", type=str, required=True, help="要渲染的文字（换行用\\n）"
    )
    parser.add_argument(
        "--font", type=str, required=True, help="字体文件路径（.ttf/.otf）"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output.png",
        help="输出图片路径（默认output.png）",
    )
    # 新增：分辨率控制
    parser.add_argument("--width", type=int, help="图片宽度（像素），不指定则自动计算")
    parser.add_argument("--height", type=int, help="图片高度（像素），不指定则自动计算")
    # 新增：对齐方式
    parser.add_argument(
        "--horizontal-align",
        type=str,
        default="center",
        choices=["left", "center", "right"],
        help="文字水平对齐（默认center）",
    )
    parser.add_argument(
        "--vertical-align",
        type=str,
        default="center",
        choices=["top", "center", "bottom"],
        help="文字垂直对齐（默认center）",
    )
    # 原有参数（优化说明）
    parser.add_argument("--font-size", type=int, default=40, help="字体大小（默认40）")
    parser.add_argument(
        "--text-color",
        type=str,
        default="0,0,0",
        help='文字颜色（RGB格式，如"255,0,0"为红色，默认黑色）',
    )
    parser.add_argument(
        "--bg-color",
        type=str,
        default="255,255,255",
        help="背景颜色（RGB格式，默认白色）",
    )
    parser.add_argument(
        "--padding", type=int, default=20, help="文字与图片边缘的间距（默认20）"
    )

    args = parser.parse_args()

    # 解析颜色参数（确保格式正确）
    try:
        text_color = tuple(map(int, args.text_color.split(",")))
        bg_color = tuple(map(int, args.bg_color.split(",")))
        assert all(0 <= c <= 255 for c in text_color) and all(
            0 <= c <= 255 for c in bg_color
        )
    except:
        print("颜色格式错误（需为0-255的RGB值，如'255,0,0'），使用默认颜色")
        text_color = (0, 0, 0)
        bg_color = (255, 255, 255)

    # 调用生成函数
    create_text_image(
        text=args.text,
        font_path=args.font,
        output_path=args.output,
        font_size=args.font_size,
        text_color=text_color,
        bg_color=bg_color,
        width=args.width,
        height=args.height,
        horizontal_align=args.horizontal_align,
        vertical_align=args.vertical_align,
        padding=args.padding,
    )


if __name__ == "__main__":
    main()
