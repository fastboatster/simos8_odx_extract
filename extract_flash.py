import xml.etree.ElementTree as ET
import binascii
import sys
import os


def bits(byte):
    return ((byte >> 7) & 1,
            (byte >> 6) & 1,
            (byte >> 5) & 1,
            (byte >> 4) & 1,
            (byte >> 3) & 1,
            (byte >> 2) & 1,
            (byte >> 1) & 1,
            (byte) & 1)


def decrypt_simos8_block(arr):
    result = bytearray()
    dupl_list = []
    for i, v in enumerate(arr):
        result.append((v ^ i) & 0xFF)
        dupl_list.append((v ^ i) & 0xFF)
        # arr[i] = (v ^ i) & 0xFF
    return result, dupl_list


test_odx = '/Users/fastboatster/Downloads/FL_8K0907551D__0003.odx'

if sys.argv[1] == 'test':
    tree = ET.parse(test_odx)
else:
    test_odx = sys.argv[1]
    tree = ET.parse(test_odx)

prefix = os.path.splitext(os.path.basename(test_odx))[0]
root = tree.getroot()
flashdata = root.findall('./FLASH/ECU-MEMS/ECU-MEM/MEM/FLASHDATAS/FLASHDATA')
fulldata = bytearray()
for data in flashdata:
    dataContent = data.findall('./DATA')[0].text
    dataId = data.get('ID')
    length = int(root.findall("./FLASH/ECU-MEMS/ECU-MEM/MEM/DATABLOCKS/DATABLOCK/FLASHDATA-REF[@ID-REF='{}']/../SEGMENTS/SEGMENT/UNCOMPRESSED-SIZE".format(dataId))[0].text)
    if len(dataContent) == 2:
        # These are ERASE blocks with no data so skip them
        continue
    list = [int(dataContent[start:start + 2], 16) for start in range(0, len(dataContent), 2)]
    # dataBinary = binascii.unhexlify(dataContent)
    decryptedContent, dupl_list = decrypt_simos8_block(list)
    fulldata.extend(decryptedContent)
    # prefix = os.path.splitext(os.path.basename(test_odx))[0]
    with open(prefix + data[0].text, 'wb') as dataFile:
        dataFile.write(decryptedContent)

with open("{}.bin".format(prefix), 'wb') as fullDataFile:
    fullDataFile.write(fulldata)