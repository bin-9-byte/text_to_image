from PIL import Image, ImageDraw, ImageFont
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
    height=None,  # 新增：图片分辨率（宽/高）
    horizontal_align="center",  # 新增：水平对齐（left/center/right）
    vertical_align="center",  # 新增：垂直对齐（top/center/bottom）
    padding=20,
):
    """创建带有特定样式的文字图片（支持分辨率、对齐方式控制）"""
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"无法加载字体文件: {font_path}")
        print("尝试使用默认字体...")
        font = ImageFont.load_default()

    # 创建临时绘图对象计算文本尺寸
    temp_img = Image.new("RGB", (1, 1), bg_color)
    temp_draw = ImageDraw.Draw(temp_img)

    # 计算平均字符宽度（用于换行）
    bbox = font.getbbox("x")
    avg_char_width = bbox[2] - bbox[0]
    # 最大每行字符数（根据图片宽度或默认最大宽度计算）
    max_line_width = width if width else 800  # 若未指定宽度，用默认800计算换行
    max_chars_per_line = (max_line_width - 2 * padding) // avg_char_width

    # 文本换行处理
    wrapped_text = []
    for paragraph in text.split("\n"):
        wrapped = textwrap.fill(paragraph, width=max_chars_per_line)
        wrapped_text.extend(wrapped.split("\n"))

    # 计算每行文本的宽高及总尺寸
    line_heights = []
    line_widths = []
    line_spacing = font_size // 4  # 行间距
    for line in wrapped_text:
        bbox = temp_draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        line_widths.append(line_width)
        line_heights.append(line_height)
    total_text_width = max(line_widths) if line_widths else 0
    total_text_height = (
        sum(line_heights) + (len(line_heights) - 1) * line_spacing
    )  # 总文字高度（含行间距）

    # 确定图片最终尺寸（优先使用用户指定的分辨率）
    if width and height:
        img_width, img_height = width, height
    else:
        # 自动计算尺寸（不超过默认最大宽度800）
        img_width = min(total_text_width + 2 * padding, 800) if not width else width
        img_height = total_text_height + 2 * padding if not height else height

    # 创建图片和绘图对象
    img = Image.new("RGB", (img_width, img_height), bg_color)
    draw = ImageDraw.Draw(img)

    # 计算文字垂直起始位置（根据垂直对齐方式）
    if vertical_align == "top":
        y_text = padding
    elif vertical_align == "center":
        # 垂直居中 = (图片高度 - 总文字高度) // 2
        y_text = (img_height - total_text_height) // 2
    else:  # bottom
        y_text = img_height - padding - total_text_height

    # 绘制每行文字（根据水平对齐方式调整x坐标）
    for i, line in enumerate(wrapped_text):
        line_width = line_widths[i]
        # 计算水平起始位置
        if horizontal_align == "left":
            x_text = padding
        elif horizontal_align == "center":
            x_text = (img_width - line_width) // 2
        else:  # right
            x_text = img_width - padding - line_width

        # 绘制文字
        draw.text((x_text, y_text), line, font=font, fill=text_color)
        # 更新下一行y坐标（当前行高 + 行间距）
        y_text += line_heights[i] + line_spacing

    img.save(output_path)
    print(f"图片已保存至: {output_path}（分辨率：{img_width}x{img_height}）")


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
