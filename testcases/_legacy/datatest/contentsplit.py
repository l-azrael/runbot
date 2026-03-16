import pandas as pd
import re


def extract_refund_and_fee(input_file_path: str, output_file_path: str):
    # 读取原始 Excel 文件
    df = pd.read_csv(input_file_path)

    # 假设需要提取的内容在 '退款信息' 列
    refund_column = '备注'
    refund_amount_column = '退款总金额'
    fee_amount_column = '手续费'

    # 正则表达式提取退款总金额和手续费
    refund_pattern = r"退款总金额([\d.]+)元"
    fee_pattern = r"含手续费([\d.]+)元"

    # 提取并填充新列
    df[refund_amount_column] = df[refund_column].apply(
        lambda x: float(re.search(refund_pattern, str(x)).group(1)) if re.search(refund_pattern, str(x)) else None)
    df[fee_amount_column] = df[refund_column].apply(
        lambda x: float(re.search(fee_pattern, str(x)).group(1)) if re.search(fee_pattern, str(x)) else None)

    # 保存修改后的 Excel 文件（覆盖原文件）
    df.to_csv(output_file_path, index=False)
    print(f"数据已提取并保存到 {output_file_path}")


if __name__ == "__main__":
    # 示例调用
    input_file = r'D:\Data\order\testa_updated1.csv'  # 输出表 B 文件路径
    output_file = input_file  # 输出文件路径为原文件
    extract_refund_and_fee(input_file, output_file)
