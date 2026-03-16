import pandas as pd


def update_datetime_format(input_file_path: str, output_file_path: str, datetime_column: str):
    # 读取 Excel 文件
    df = pd.read_csv(input_file_path)

    # 将时间列转换为 datetime 类型
    df[datetime_column] = pd.to_datetime(df[datetime_column], errors='coerce')  # 将错误的数据转换为 NaT

    # 将时间格式修改为 'YYYY-MM-DD HH:MM:SS'，并创建新列
    df['时间格式化'] = df[datetime_column].dt.strftime('%Y-%m-%d %H:%M:%S')

    # 保存修改后的 Excel 文件
    df.to_csv(output_file_path, index=False)
    print(f"数据已更新并保存到 {output_file_path}")


if __name__ == "__main__":
    # 示例调用
    input_file = r'D:\Data\order\testa_updated1.csv'  # 输出表 B 文件路径
    output_file = input_file  # 输出文件路径为原文件
    datetime_column = '订单结束时间'  # 假设时间列的列名为 '时间列'
    update_datetime_format(input_file, output_file, datetime_column)
