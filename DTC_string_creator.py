from tkinter import filedialog
from tkinter import messagebox as mb

from pandas import DataFrame

from DTC_parser import get_df_from_questionary, dtc_3_byte_to_hex, get_df_from_dtc_layout

xmlns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
xmlns_xsd = "http://www.w3.org/2001/XMLSchema"
start_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<DTCpool xmlns_xsi="{xmlns_xsi}" xmlns_xsd="{xmlns_xsd}">
'''
end_xml = '</DTCpool>'

number = 1


class DTC(object):
    def __init__(self):
        self._hex_code_string = '0x000000'
        self._code = 'P000000'
        self._name_EN = 'Not defined'
        self._name_RU = 'Нет описания'
        self._name_CH = '没有定义的'
        self._xml = ''
        self._repair_desc_en = ''
        self._repair_desc_ru = ''

    @property
    def hex_code_string(self):
        return self._hex_code_string

    @hex_code_string.setter
    def hex_code_string(self, value):
        self._hex_code_string = value

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value

    @property
    def name_en(self):
        return self._name_EN

    @name_en.setter
    def name_en(self, value):
        self._name_EN = value

    @property
    def name_ru(self):
        return self._name_RU

    @name_ru.setter
    def name_ru(self, value):
        self._name_RU = value

    @property
    def name_ch(self):
        return self._name_CH

    @name_ch.setter
    def name_ch(self, value):
        self._name_CH = value

    @property
    def repair_desc_en(self):
        return self._repair_desc_en

    @repair_desc_en.setter
    def repair_desc_en(self, value):
        self._repair_desc_en = value

    @property
    def repair_desc_ru(self):
        return self._repair_desc_ru

    @repair_desc_ru.setter
    def repair_desc_ru(self, value):
        self._repair_desc_ru = value

    #             <hex_code>{dtc_3_byte_to_hex(self._code)}</hex_code>
    # < titleCH > ({self._code})
    # {self._name_CH} < / titleCH >

    @property
    def xml(self):
        self._xml = f'''
                <ecode>{self._hex_code_string}</ecode>
                <titleEN>({self._code}){self._name_EN}</titleEN>
                <titleRU>({self._code}){self._name_RU}</titleRU>
                <spn></spn>
                <fmi></fmi>
                <RepairActionEN>{self._repair_desc_en}</RepairActionEN>
                <RepairActionRU>{self._repair_desc_ru}</RepairActionRU>
                <IgnoreDTCStations></IgnoreDTCStations>
        '''
        return self._xml

    def xml_with_number(self, value):
        xml_number = f'''        <DTC Number="{value}">{self.xml}</DTC>
'''
        return xml_number


def xml_file_writer(file_name: str, line_list) -> None:
    try:
        with open(file_name, "w", encoding='utf-8') as file:
            file.writelines(line_list)

    except Exception as exception:
        raise exception


def define_file_type(file_name: str) -> DataFrame:
    try:
        dtc_df = get_df_from_questionary(file_name)
    except UserWarning:
        try:
            dtc_df = get_df_from_dtc_layout(file_name)
        except UserWarning as e:
            raise UserWarning("Can't determine neither Diagnostic_Questionnaire nor DTCs_Layout file")
    return dtc_df


if __name__ == '__main__':
    file_location = filedialog.askopenfilename(filetypes=[("Excel files", ".xlsx")])

    try:
        dtc_df = define_file_type(file_location)
        exit_xml = start_xml
        j = 1
        for dtc in dtc_df.iloc:
            # it's necessary to check that there are all fields in the dtc
            dtc_dict = dtc.to_dict()
            i = DTC()
            i.code = dtc_dict.get('3-Bytes DTC', 'DTC Code is Not Defined')
            # i.hex_code_string = dtc_dict.get('Hex Value\n[hex]', dtc_3_byte_to_hex(i.code))
            i.hex_code_string = dtc_3_byte_to_hex(i.code)
            i.name_en = dtc_dict.get('English', "Description isn't found")
            i.name_ru = dtc_dict.get('Russian', "Описание ошибки не найдено")
            i.name_ch = dtc_dict.get('Chinese', "未找到错误描述")
            i.repair_desc_en = dtc_dict.get('Repair action', '')
            i.repair_desc_ru = dtc_dict.get('Repair action Russian', '')
            exit_xml += i.xml_with_number(j)
            j += 1
        exit_xml += end_xml
        ecu_name = file_location.split('ATOM_')[1].split('_')[0]
        xml_file_writer(f'DTC_{ecu_name}_xml.xml', exit_xml)
    except Exception as ex:
        mb.showerror(title='Alarm', message=str(ex))
