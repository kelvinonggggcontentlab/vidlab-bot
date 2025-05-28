import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheetClient:
    def __init__(self, creds_json_path: str, spreadsheet_id: str):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json_path, scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(spreadsheet_id)

    def get_sheet(self, sheet_name: str):
        return self.sheet.worksheet(sheet_name)

    def get_all_records(self, sheet_name: str):
        worksheet = self.get_sheet(sheet_name)
        return worksheet.get_all_records()

    def find_rows_by_condition(self, sheet_name: str, column_name: str, value, processed_col_name=None, processed_flag=None):
        """
        查询指定列值匹配，并且可选过滤未处理的行
        返回符合条件的所有行字典列表
        """
        worksheet = self.get_sheet(sheet_name)
        records = worksheet.get_all_records()

        result = []
        for idx, row in enumerate(records, start=2):  # gspread行号从2开始（标题在1）
            if row.get(column_name) == value:
                if processed_col_name and processed_flag is not None:
                    if row.get(processed_col_name) == processed_flag:
                        result.append({'row_num': idx, **row})
                else:
                    result.append({'row_num': idx, **row})
        return result

    def update_row(self, sheet_name: str, row_num: int, updates: dict):
        """
        根据行号更新对应列的值
        updates格式：{"列名": "新值"}
        """
        worksheet = self.get_sheet(sheet_name)
        headers = worksheet.row_values(1)
        for col_name, value in updates.items():
            if col_name in headers:
                col_index = headers.index(col_name) + 1
                worksheet.update_cell(row_num, col_index, value)

    def append_row(self, sheet_name: str, row_values: list):
        worksheet = self.get_sheet(sheet_name)
        worksheet.append_row(row_values)

    # 以下是针对Vidlab自动剪辑流程常用的表操作方法

    def get_pending_footage(self, sheet_name: str, status_col='Video Status', status_value='Uploaded', processed_col='Processed', processed_flag='NO'):
        """
        获取状态为Uploaded且未处理的素材记录列表
        返回包含Google Sheet行号的字典列表
        """
        worksheet = self.get_sheet(sheet_name)
        records = worksheet.get_all_records()

        pending = []
        for idx, row in enumerate(records, start=2):
            if row.get(status_col) == status_value and row.get(processed_col) == processed_flag:
                pending.append({'row_num': idx, **row})
        return pending

    def mark_footage_processed(self, sheet_name: str, row_num: int, v_code: str, output_path: str, processed_col='Processed'):
        """
        更新素材行标记为已处理，写入V_CODE和输出路径
        """
        updates = {
            processed_col: 'YES',
            'V CODE': v_code,
            'Final Output File Path': output_path,
            'Video Status': 'Processed'
        }
        self.update_row(sheet_name, row_num, updates)

    def add_v_code_log(self, sheet_name: str, row_data: dict):
        """
        新增V CODE日志记录行，row_data为字段顺序对应的列表或字典，
        需确保字段和表头一致
        """
        worksheet = self.get_sheet(sheet_name)
        headers = worksheet.row_values(1)

        if isinstance(row_data, dict):
            # 按headers顺序填充对应数据
            row_values = [row_data.get(h, '') for h in headers]
        elif isinstance(row_data, list):
            row_values = row_data
        else:
            raise ValueError('row_data必须是dict或list类型')

        worksheet.append_row(row_values)


# 以下为示例用法
if __name__ == '__main__':
    client = GoogleSheetClient('vidlab-marketing-460409-f0e918ae72e2.json', '你的SheetID')
    footage = client.get_pending_footage('Footage Log')
    print('待处理素材:', footage)

    # 更新示例
    if footage:
        first = footage[0]
        client.mark_footage_processed('Footage Log', first['row_num'], 'G003_V0001', '/Final Video/path.mp4')

    # 添加V CODE日志示例
    client.add_v_code_log('V Code Log', {
        'M CODE': 'G003_M0001',
        'V CODE': 'G003_V0001',
        'Final Output File Path': '/Final Video/path.mp4',
        'Status': 'Ready for approval'
    })
