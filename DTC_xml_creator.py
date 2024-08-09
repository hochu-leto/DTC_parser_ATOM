import xml.etree.ElementTree as ET

from DTC_string_creator import xmlns_xsi, xmlns_xsd

root = ET.Element('DTCpool')
root.text = f'xmlns_xsi="{xmlns_xsi}" xmlns_xsd="{xmlns_xsd}"'
tree = ET.ElementTree(root)
tree.write('DTC.xml')
