from tkinter import filedialog
import pandas as pd
from deep_translator import GoogleTranslator
from sys import stdout

from pandas import Series, DataFrame

DTC = 'DTC'
DTC_Layout = 'DTCs Layout'
column_name_for_translate = 'DTC Name'
word_in_column_name_for_delete = 'Self-healing'
language_to_translate = 'Russian'
translated_file_name = 'DTC.xlsx'
dict_of_languages = dict(Russian='ru', English='en', Chinese='zh-TW')
russian_description_list = list()
russian_repair_actions_list = list()
english_repair_actions_list = list()
language = 'English'
dtc_char_to_byte_dict = dict(
    P=0b00,
    C=0b01,
    B=0b10,
    U=0b11
)
dtc_layout_headers = dict(

    DTC_Display='DTC Display',
    DTC_Description='DTC Description',
    Repair_action='Repair action',
    DTC_Number='DTC Number')
english_description_list = list()
ibs_chinese_dtc_list = list()
cjk_ranges = [
    (0x4E00, 0x62FF),
    (0x6300, 0x77FF),
    (0x7800, 0x8CFF),
    (0x8D00, 0x9FCC),
    (0x3400, 0x4DB5),
    (0x20000, 0x215FF),
    (0x21600, 0x230FF),
    (0x23100, 0x245FF),
    (0x24600, 0x260FF),
    (0x26100, 0x275FF),
    (0x27600, 0x290FF),
    (0x29100, 0x2A6DF),
    (0x2A700, 0x2B734),
    (0x2B740, 0x2B81D),
    (0x2B820, 0x2CEAF),
    (0x2CEB0, 0x2EBEF),
    (0x2F800, 0x2FA1F)
]


def check_dtc_display(dtc_code: str) -> str:
    dtc_code = dtc_code.strip()
    if ' ' in dtc_code:
        for s in dtc_code.split(' '):
            if s[0] in list(dtc_char_to_byte_dict.keys()):
                return s
    elif dtc_code[0] in list(dtc_char_to_byte_dict.keys()):
        return dtc_code.strip()
    raise UserWarning(f'DTC Display {dtc_code} is incorrect')


def dtc_display(dtc_series: Series, df_dtc_sheet: DataFrame) -> DataFrame:
    stdout.write('Checking the DTC Display...\n')
    dtc_list = list()
    for i in dtc_series:
        dtc = ''
        try:
            dtc = check_dtc_display(i)
        except UserWarning as ex:
            dtc = str(ex)
            print(str(ex))
        finally:
            dtc_list.append(dtc)
    # это, конечно, порнуха
    df_dtc_sheet['3-Bytes DTC'] = dtc_list
    df_dtc_sheet['Hex Value\n[hex]'] = [dtc_3_byte_to_hex(i) for i in dtc_list]
    return df_dtc_sheet


def dtc_description(list_dtc_for_translate: Series, df_dtc_sheet: DataFrame) -> DataFrame:
    stdout.write('Checking the DTC Description...\n')
    j, ln = 0, len(list_dtc_for_translate)
    for dtc_for_translate in list_dtc_for_translate:
        j += 1
        stdout.write(f' \rTranslating {j} from {ln} Descriptions')
        stdout.flush()
        only_china_text = [i for i in dtc_for_translate.split() if is_str_cjk(i)]
        only_english_text = [i for i in dtc_for_translate.split() if not is_str_cjk(i) and '_' not in i]

        english_dtc_description = ' '.join(only_english_text) if only_english_text else ' '.join([
            GoogleTranslator(source=dict_of_languages['Chinese'],
                             target=dict_of_languages[language]).translate(i) for i in only_china_text])

        english_description_list.append(english_dtc_description)
        russian_description_list.append(GoogleTranslator(source=dict_of_languages[language],
                                                         target=dict_of_languages[language_to_translate]
                                                         ).translate(english_dtc_description))
    df_dtc_sheet[language_to_translate] = russian_description_list
    df_dtc_sheet['English'] = english_description_list
    stdout.write("\n")
    return df_dtc_sheet


def repair_actions(list_repair_for_translate: Series, df_dtc_sheet: DataFrame) -> DataFrame:
    stdout.write('Checking the Repair action...\n')
    j, ln = 0, len(list_repair_for_translate)
    for repair_for_translate in list_repair_for_translate:
        j += 1
        stdout.write(f' \rTranslating {j} from {ln} Repair action')
        stdout.flush()
        if str(repair_for_translate) == 'nan':
            english_repair_actions = ''
        else:
            english_sentence = [i for i in repair_for_translate.split() if
                                not is_str_cjk(i)]
            english_repair_actions = ' '.join(english_sentence)

        english_repair_actions_list.append(english_repair_actions)
        russian_repair_actions_list.append(GoogleTranslator(source=dict_of_languages[language],
                                                            target=dict_of_languages[language_to_translate]
                                                            ).translate(english_repair_actions))

    df_dtc_sheet['Repair action Russian'] = russian_repair_actions_list
    df_dtc_sheet['Repair action'] = english_repair_actions_list
    stdout.write("\n")
    return df_dtc_sheet


def save_dataframe(df_dtc_sheet: DataFrame):
    try:
        with pd.ExcelWriter(
                translated_file_name,
                engine="xlsxwriter",
                mode='w') as excel_writer:

            df_dtc_sheet.to_excel(excel_writer, sheet_name='Translated', header=True, index=False)
    except PermissionError:
        raise PermissionError(f"Close the {translated_file_name} and try again")


def is_cjk(char):
    char = ord(char)
    for bottom, top in cjk_ranges:
        if bottom <= char <= top:
            return True
    return False


def is_str_cjk(st: str) -> bool:
    for ch in st:
        if is_cjk(ch):
            return True
    return False


def get_df_from_questionary(file_locate: str) -> pd.DataFrame:
    if DTC in pd.ExcelFile(file_locate).sheet_names:
        df_dtc_sheet = pd.read_excel(file_locate, sheet_name=DTC)
        for dtc in df_dtc_sheet.items():
            if dtc[0] == column_name_for_translate:
                list_dtc_for_translate = dtc[1]
                language = list_dtc_for_translate[0]
                russian_description_list.append(language_to_translate)
                for dtc_for_translate in list_dtc_for_translate[1:]:
                    russian_description_list.append(GoogleTranslator(source=dict_of_languages[language],
                                                                     target=dict_of_languages[language_to_translate]
                                                                     ).translate(dtc_for_translate))
            elif word_in_column_name_for_delete in dtc[0]:
                del df_dtc_sheet[dtc[0]]
        df_dtc_sheet[language_to_translate] = russian_description_list
        df_dtc_sheet.columns = df_dtc_sheet.iloc[0]
        df_dtc_sheet = df_dtc_sheet.iloc[1:, :]
        try:
            with pd.ExcelWriter(
                    translated_file_name,
                    engine="xlsxwriter",
                    mode='w') as excel_writer:

                df_dtc_sheet.to_excel(excel_writer, sheet_name='Translated', header=True, index=False)
        except PermissionError:
            raise PermissionError(f"Close the {translated_file_name} and try again")
        finally:
            return df_dtc_sheet
    raise UserWarning(f'There is no {DTC} sheet in this document, please check')


def check_str_in_sheets(file: str) -> DataFrame | None:
    for sheet in pd.ExcelFile(file).sheet_names:
        if DTC_Layout in sheet:
            return pd.read_excel(file, sheet_name=sheet, index_col=1, header=1)
    return None


def get_df_from_dtc_layout(file_locate: str) -> pd.DataFrame:
    dtc_sheet = check_str_in_sheets(file_locate)

    if dtc_sheet is not None:
        for dtc in dtc_sheet.items():
            if (dtc_layout_headers['DTC_Display'] in dtc[0] or
                    dtc_layout_headers['DTC_Number'] in dtc[0]):  # DTC Display -> 3-Bytes DTC code + HEX code DTC
                # we don't need DTC without DTC code - field "DTC Display"
                dtc_sheet.dropna(subset=[dtc[0]], inplace=True)
                dtc_sheet = dtc_display(dtc_sheet[dtc[0]], dtc_sheet)
            elif dtc_layout_headers['DTC_Description'] in dtc[0]:  # DTC Description
                dtc_sheet = dtc_description(dtc[1], dtc_sheet)
            elif dtc_layout_headers['Repair_action'] in dtc[0]:  # DTC Repair action
                dtc_sheet = repair_actions(dtc[1], dtc_sheet)
            del dtc_sheet[dtc[0]]
        save_dataframe(dtc_sheet)
        return dtc_sheet
    raise UserWarning(f'There is no {DTC_Layout} sheet in this document, please check')


def dtc_3_byte_to_hex(dtc_3_byte: str) -> str:  # string in HEX without "0x"
    first_symbol = dtc_3_byte[0]
    dtc_value = dtc_3_byte[1:]
    first_bit = dtc_char_to_byte_dict.get(first_symbol, 0)
    first_bit = first_bit << 22
    try:
        value = int(dtc_value.ljust(6, '0'), 16)
        hex_code = hex(value + first_bit)
    except ValueError as exception:
        print(f'Incorrect 3-Bytes DTC -> {dtc_value}')
        hex_code = hex(0)
    # If full HEX with '0x' needs use this
    # hex_code = '0x' + hex_code[2:].upper()
    hex_code = hex_code[2:].upper()
    return hex_code[:6]


if __name__ == '__main__':
    file_location = filedialog.askopenfilename(
        filetypes=[("Excel files", ".xlsx")],
    )
    # print(get_df_from_questionary(file_location)['Chinese'])
    print(get_df_from_dtc_layout(file_location))
