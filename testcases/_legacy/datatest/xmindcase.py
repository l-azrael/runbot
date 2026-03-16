import zipfile
import xml.etree.ElementTree as ET
import os
import openpyxl


def parse_xmind(input_file, output_excel_file):
    # 解压 XMind 文件
    with zipfile.ZipFile(input_file, 'r') as zip_ref:
        zip_ref.extractall('temp_xmind')

    # 检查解压后的文件结构
    print("解压后的文件结构：")
    for root, dirs, files in os.walk('temp_xmind'):
        for file in files:
            print(os.path.join(root, file))

    # 解析 content.xml 文件
    content_file = r'temp_xmind\content.xml'
    if not os.path.exists(content_file):
        # 如果默认路径没有找到，尝试其他可能的路径
        content_file = 'temp_xmind/xmind/contents.xml'

    if not os.path.exists(content_file):
        raise FileNotFoundError(f"没有找到 content.xml 文件，当前路径：{content_file}")

    # 解析 XML 内容
    tree = ET.parse(content_file)
    root = tree.getroot()

    # 定义命名空间
    ns = {'x': 'urn:xmind:xmap:xmlns:content:1.0'}

    # 获取所有根节点的主题
    topics = root.findall('.//x:topic', ns)

    # 创建 Excel 文件并写入数据
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Test Cases"

    # 初始化列标题
    headers = ["用例目录", "用例标题"]
    ws.append(headers)

    # 用于递归遍历主题的函数
    def traverse_topic(topic, path=[]):
        # 获取当前主题的标题
        title = topic.find('./x:title', ns)
        if title is not None:
            title_text = title.text.strip() if title.text else ""

            # 如果是叶子节点（没有子节点），则为用例标题
            if len(topic.findall('./x:topics/x:topic', ns)) == 0:
                # 生成用例目录（路径）和标题
                case_directory = "/".join(path)  # 目录路径
                case_title = title_text  # 用例标题
                ws.append([case_directory, case_title])
            else:
                # 非叶子节点，递归遍历子节点
                path.append(title_text)
                for subtopic in topic.findall('./x:topics/x:topic', ns):
                    traverse_topic(subtopic, path.copy())

    # 遍历所有的根节点
    for topic in topics:
        traverse_topic(topic)

    # 保存到 Excel 文件
    wb.save(output_excel_file)

    # 清理临时文件夹
    for root, dirs, files in os.walk('temp_xmind', topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))


if __name__ == "__main__":
    input_xmind_file = r'C:\Users\wangz\Downloads\1.3.116直播推流回放方案.xmind'  # 输入XMind文件路径
    output_excel_file = r'C:\Users\wangz\Downloads\output_test_cases.xlsx'  # 输出Excel文件路径

    parse_xmind(input_xmind_file, output_excel_file)
    print(f"XMind 文件已成功解析并保存为 Excel：{output_excel_file}")
