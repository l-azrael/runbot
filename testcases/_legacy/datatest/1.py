import pandas as pd


def match_and_update(input_file_a: str, input_file_b: str, output_file_a: str, output_file_b: str):
    # 读取表 A 和表 B 的 CSV 文件
    df_a = pd.read_csv(input_file_a)
    df_b = pd.read_csv(input_file_b)

    # 确保退款总金额为浮动类型并转换记账时间和订单结束时间的格式
    df_a['退款总金额'] = df_a['退款总金额'].astype(float)
    df_b['退款总金额'] = df_b['退款总金额'].astype(float)

    # 将时间列转换为 datetime 类型，统一格式
    df_a['记账时间'] = pd.to_datetime(df_a['记账时间'], errors='coerce')
    df_b['订单结束时间'] = pd.to_datetime(df_b['订单结束时间'], errors='coerce')

    # 创建 "是否存在" 列，如果不存在
    if '是否存在' not in df_a.columns:
        df_a['是否存在'] = 'no'
    if '是否存在' not in df_b.columns:
        df_b['是否存在'] = 'no'

    # 遍历表 B 的每一行进行匹配
    for index_b, row_b in df_b.iterrows():
        # 获取表 B 的退款总金额和订单结束时间
        refund_b = row_b['退款总金额']
        order_end_time_b = row_b['订单结束时间']

        # 在表 A 中查找匹配的退款总金额
        matching_row_a = df_a[df_a['退款总金额'] == refund_b]

        if not matching_row_a.empty:
            # 对比记账时间（年月日时分）
            for index_a, row_a in matching_row_a.iterrows():
                account_time_a = row_a['记账时间']

                print(f"A {account_time_a}")
                print(f"B {order_end_time_b}")
                # 只取年月日时分部分
                if account_time_a.strftime('%Y-%m-%d %H:%M') == order_end_time_b.strftime('%Y-%m-%d %H:%M'):
                    # 更新表 B 中的 "是否存在" 和 "记账时间" 列
                    df_b.at[index_b, '是否存在'] = 'yes'
                    df_b.at[index_b, '记账时间'] = row_a['记账时间']

                    # 在表 A 中的 "是否存在" 列也更新为 "yes"
                    df_a.at[index_a, '是否存在'] = 'yes'

    # 保存更新后的表 A 和表 B（CSV 格式）
    df_a.to_csv(output_file_a, index=False)
    df_b.to_csv(output_file_b, index=False)
    print(f"数据已更新并保存到 {output_file_a} 和 {output_file_b}")


if __name__ == "__main__":
    # 示例调用
    input_file_a = r'D:\Data\order\testa_updated1.csv'  # 表 A 输入文件路径
    input_file_b = r'D:\Data\order\testb_updated2.csv'  # 表 B 输入文件路径
    output_file_a = r'D:\Data\order\testa_updated_result.csv'  # 输出表 A 文件路径
    output_file_b = r'D:\Data\order\testb_updated_result.csv'  # 输出表 B 文件路径
    match_and_update(input_file_a, input_file_b, output_file_a, output_file_b)
