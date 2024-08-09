from tkinter import filedialog

import pandas as pd
from deep_translator import GoogleTranslator

DTC = 'DTC'
DTC_Layout = 'DTCs Layout'
column_name_for_translate = 'DTC Name'
word_in_column_name_for_delete = 'Self-healing'
language_to_translate = 'Russian'
translated_file_name = 'DTC.xlsx'
dict_of_languages = dict(Russian='ru', English='en', Chinese='zh-TW')
list_for_translated_dtc = list()
list_for_translated_repair = list()
list_for_english_repair = list()
language = 'English'
dtc_char_to_byte_dict = dict(
    P=0b00,
    C=0b01,
    B=0b10,
    U=0b11
)
dtc_layout_headers_list_to_df = ['DTC Display', 'DTC Description', 'Repair action']
ibs_english_dtc_list = list()
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
                list_for_translated_dtc.append(language_to_translate)
                for dtc_for_translate in list_dtc_for_translate[1:]:
                    list_for_translated_dtc.append(GoogleTranslator(source=dict_of_languages[language],
                                                                    target=dict_of_languages[language_to_translate]
                                                                    ).translate(dtc_for_translate))
            elif word_in_column_name_for_delete in dtc[0]:
                del df_dtc_sheet[dtc[0]]
        df_dtc_sheet[language_to_translate] = list_for_translated_dtc
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


def get_df_from_dtc_layout(file_locate: str) -> pd.DataFrame:
    if DTC_Layout in pd.ExcelFile(file_locate).sheet_names:
        df_dtc_sheet = pd.read_excel(file_locate, sheet_name=DTC_Layout, index_col=1, header=1)
        for dtc in df_dtc_sheet.items():
            if dtc_layout_headers_list_to_df[1] in dtc[0]:
                list_dtc_for_translate = dtc[1]

                for dtc_for_translate in list_dtc_for_translate:
                    # only for IBS
                    ibs_lang_list = list(filter(None, dtc_for_translate.split('\n')))
                    ibs_dtc_chinese_description = ibs_lang_list[1]
                    ibs_dtc_english_description = ibs_lang_list[2] if len(ibs_lang_list) >= 3 else \
                        GoogleTranslator(source=dict_of_languages['Chinese'],
                                         target=dict_of_languages[language]).translate(ibs_dtc_chinese_description)
                    ibs_english_dtc_list.append(ibs_dtc_english_description)
                    ibs_chinese_dtc_list.append(ibs_dtc_chinese_description)
                    list_for_translated_dtc.append(GoogleTranslator(source=dict_of_languages[language],
                                                                    target=dict_of_languages[language_to_translate]
                                                                    ).translate(ibs_dtc_english_description))
                df_dtc_sheet[language_to_translate] = list_for_translated_dtc
                df_dtc_sheet['English'] = ibs_english_dtc_list
                df_dtc_sheet['Chinese'] = ibs_chinese_dtc_list
            elif dtc_layout_headers_list_to_df[0] in dtc[0]:
                # это, конечно, порнуха
                df_dtc_sheet['3-Bytes DTC'] = dtc[1]
                df_dtc_sheet['Hex Value\n[hex]'] = [dtc_3_byte_to_hex(i) for i in dtc[1]]
            elif dtc_layout_headers_list_to_df[2] in dtc[0]:
                list_repair_for_translate = dtc[1]
                for repair_for_translate in list_repair_for_translate:
                    english_sentence = [i for i in repair_for_translate.split() if
                                     not is_str_cjk(i)]
                    english_desc = ' '.join(english_sentence)
                    list_for_english_repair.append(english_desc)
                    list_for_translated_repair.append(GoogleTranslator(source=dict_of_languages[language],
                                                                       target=dict_of_languages[language_to_translate]
                                                                       ).translate(english_desc))

                df_dtc_sheet['Repair action Russian'] = list_for_translated_repair
                df_dtc_sheet['Repair action'] = list_for_english_repair

            del df_dtc_sheet[dtc[0]]
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
        print('Incorrect 3-Bytes DTC')
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
