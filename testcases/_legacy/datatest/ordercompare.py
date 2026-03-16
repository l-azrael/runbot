import pandas as pd


def match_and_update_excel(file_a: str, file_b: str, output_file_a: str, output_file_b: str):
    """
    从表 B 的 '支付单号' 列遍历，查找在表 A 中是否存在匹配的 '业务凭证号'。
    如果存在，表 A 和表 B 中的 '是否存在' 列更新为 'yes'，否则更新为 'no'。

    参数:
    file_a (str): 表 A 的 Excel 文件路径
    file_b (str): 表 B 的 Excel 文件路径
    output_file_a (str): 输出的表 A Excel 文件路径（包含更新后的 "是否存在" 列）
    output_file_b (str): 输出的表 B Excel 文件路径（包含更新后的 "是否存在" 列）
    """

    # 读取表 A 和表 B
    df_a = pd.read_excel(file_a)
    df_b = pd.read_excel(file_b)

    # # 确保 "业务凭证号" 和 "支付单号" 列的数据类型为字符串
    # df_a['业务凭证号'] = df_a['业务凭证号'].astype(str)
    # df_b['支付单号'] = df_b['支付单号'].astype(str)

    # 检查表 A 中是否已有 "是否存在" 列，如果没有，则创建该列，初始值为 "no"
    if '是否存在' not in df_a.columns:
        df_a['是否存在'] = 'no'

    # 检查表 B 中是否已有 "是否存在" 列，如果没有，则创建该列，初始值为 "no"
    if '是否存在' not in df_b.columns:
        df_b['是否存在'] = 'no'

    # 遍历表 B 的 "支付单号" 列
    for index_b, payment_id in df_b["支付单号"].items():
        # 在表 A 的 "业务凭证号" 列中查找匹配项
        match = df_a[df_a["业务凭证号"] == payment_id]
        if not match.empty:
            # 如果找到匹配项，更新表 A 和表 B 的 "是否存在" 列为 "yes"
            df_a.loc[match.index, "是否存在"] = "yes"
            df_b.loc[index_b, "是否存在"] = "yes"
            # 将表 B 中对应行的 "订单结束时间" 写入表 A 中对应的行
            df_a.loc[match.index, "订单结束时间"] = df_b.loc[index_b, "订单结束时间"]
            df_b.loc[index_b, "记账时间"] = df_a.loc[match.index, "记账时间"].values[0]
        else:
            # 如果没有找到匹配项，更新表 B 的 "是否存在" 列为 "no"
            df_b.loc[index_b, "是否存在"] = "no"

    # # 遍历表 B 的 "支付单号" 列，查找对应的表 A 数据
    # for index_b, row_b in df_b.iterrows():
    #     payment_order_number = row_b['支付单号']
    #     print(payment_order_number)
    #     # 在表 A 的 "业务凭证号" 列中查找匹配
    #     matching_row_a = df_a[df_a['业务凭证号'] == payment_order_number]
    #     print(matching_row_a)
    #     if not matching_row_a.empty:
    #         # 如果找到匹配，更新表 A 和表 B 中当前行的 "是否存在" 列为 "yes"
    #         df_a.at[matching_row_a.index[0], '是否存在'] = 'yes'
    #         df_b.at[index_b, '是否存在'] = 'yes'
        # else:
        #     # 如果没有找到匹配，更新表 A 和表 B 中当前行的 "是否存在" 列为 "no"
        #     df_a.at[matching_row_a.index[0], '是否存在'] = 'no' if not matching_row_a.empty else 'no'
        #     df_b.at[index_b, '是否存在'] = 'no'

    try:
        df_a.to_csv(output_file_a, index=False)
        df_b.to_csv(output_file_b, index=False)
        print(f"表 A 和表 B 已更新并保存到 {output_file_a} 和 {output_file_b}")
    except Exception as e:
        print(f"保存文件时出错: {e}")


# 调用函数，文件路径是 'D:\\Data\\order\\wxorder.xlsx' 和 'D:\\Data\\order\\1739929243907.xlsx'
# if __name__ == "__main__":
#     # 请确保文件路径正确，并替换为实际的时间段
#     file_a = r'D:\Data\order\wxorder.xlsx'  # 表 A 文件路径
#     file_b = r'D:\Data\order\1739929243907.xlsx'  # 表 B 文件路径
#     output_file_a = r'D:\Data\order\wxorder_updated.xlsx'  # 输出表 A 文件路径
#     output_file_b = r'D:\Data\order\1739929243907_updated.xlsx'  # 输出表 B 文件路径
#
#     match_and_update_excel(file_a, file_b, output_file_a, output_file_b)

if __name__ == "__main__":
    # 请确保文件路径正确，并替换为实际的时间段
    file_a = r'D:\Data\order\wxorder.xlsx'  # 表 A 文件路径
    file_b = r'D:\Data\order\1739929243907.xlsx'  # 表 B 文件路径
    output_file_a = r'D:\Data\order\testa_updated.csv'  # 输出表 A 文件路径
    output_file_b = r'D:\Data\order\testb_updated.csv'  # 输出表 B 文件路径

    match_and_update_excel(file_a, file_b, output_file_a, output_file_b)

