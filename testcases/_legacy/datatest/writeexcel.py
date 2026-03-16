import pandas as pd
from datetime import datetime, timedelta


def get_assigned_date(end_time: datetime, time_range_start: datetime, time_range_end: datetime) -> datetime.date:
    """
    判断订单的结束时间应归属到哪个日期。
    每日的时间段为 05:00 - 05:00，订单结束时间若在当前时间段内，归属到时间段开始日期。

    参数:
    end_time (datetime): 订单的结束时间
    time_range_start (datetime): 当前时间段的开始时间
    time_range_end (datetime): 当前时间段的结束时间

    返回:
    datetime.date: 订单归属的日期
    """
    # 判断结束时间是否在当前时间段内，如果不在，更新时间段
    while end_time >= time_range_end:
        time_range_start += timedelta(days=1)
        time_range_end += timedelta(days=1)

    return time_range_start.date()


def calculate_order_total_by_end_date(excel_file: str, time_range_start: str, time_range_end: str, output_file: str):
    """
    解析 Excel 文件，根据订单的结束时间归属到指定时间段，并计算每天的订单总金额。

    参数:
    excel_file (str): Excel 文件路径
    time_range_start (str): 时间段开始时间（如 '2025-01-26 05:00'）
    time_range_end (str): 时间段结束时间（如 '2025-01-27 05:00'）
    output_file (str): 输出文件路径（Excel）

    返回:
    pandas.DataFrame: 每天订单总金额统计
    """
    # 读取 Excel 文件
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        print(f"Error reading the Excel file: {e}")
        return

    # 确保列名与实际文件中的列名一致
    # 假设列名为 'order_amount' 和 'end_time'

    # 转换 'end_time' 列为 datetime 格式
    df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce')

    # 检查是否有无效的日期数据
    if df['end_time'].isnull().any():
        print("Warning: There are invalid date formats in the 'end_time' column.")

    # 转换时间段的开始和结束为 datetime
    try:
        time_range_start = pd.to_datetime(time_range_start)
        time_range_end = pd.to_datetime(time_range_end)
    except ValueError as e:
        print(f"Invalid time range format: {e}")
        return

    # 为每条订单记录分配归属日期
    df['assigned_date'] = df['end_time'].apply(get_assigned_date, time_range_start=time_range_start,
                                               time_range_end=time_range_end)

    # 按归属日期分组并计算订单金额总数
    daily_total = df.groupby('assigned_date')['order_amount'].sum().reset_index()

    # 打印每日订单总金额
    print(daily_total)

    # 保存为 Excel 文件
    try:
        daily_total.to_excel(output_file, index=False)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving the results to Excel: {e}")


# 调用函数，文件路径是 'C:\\Users\\wangz\\Desktop\\order.xlsx'
if __name__ == "__main__":
    # 请确保文件路径正确，并替换为实际的时间段
    excel_file = r'C:\Users\wangz\Desktop\order.xlsx'  # 使用原始字符串来避免路径中的转义字符问题
    time_range_start = '2025-01-25 00:00'
    time_range_end = '2025-01-26 00:00'
    output_file = r'C:\Users\wangz\Desktop\daily_order_totals.xlsx'  # 输出 Excel 文件路径

    output_file = r'D:\AutoTest\QGAutoDemo\apis\eshop\api'  # 输出 Excel 文件路径



    calculate_order_total_by_end_date(excel_file, time_range_start, time_range_end, output_file)


