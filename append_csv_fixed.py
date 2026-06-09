import csv, base64

csv_path = r'd:\RE4_VietHoa\vietnamese_translation.csv'
new_rows = [
    {
        'File Path': r'natives\stm\_chainsaw\message\mes_main_sys\ch_mes_main_sys_tutorial.msg.22',
        'Entry Name': 'CH_Mes_Main_Sys_TutorialBody_005',
        'Entry Index': '11',
        'English': '<ICON CROUCH> Crouch / Stand',
        'Vietnamese': b'<ICON CROUCH> Ng\xe1\xbb\x93i / \xc4\x90\xe1\xbb\xa9ng'.decode('utf-8')
    },
    {
        'File Path': r'natives\stm\_chainsaw\message\mes_main_file\ch_mes_main_file_038.msg.22',
        'Entry Name': 'CH_Mes_Main_File_038_00',
        'Entry Index': '0',
        'English': 'Crude Charm',
        'Vietnamese': b'B\xc3\xb9a th\xc3\xb4'.decode('utf-8')
    },
    {
        'File Path': r'natives\stm\_chainsaw\message\mes_main_file\ch_mes_main_file_038.msg.22',
        'Entry Name': 'CH_Mes_Main_File_038_01',
        'Entry Index': '1',
        'English': '"Judgment is Nigh"',
        'Vietnamese': b'"S\xe1\xbb\xb1 ph\xc3\xa1n x\xc3\xa9t \xc4\x91\xc3\xa3 c\xe1\xba\xadn k\xe1\xbb\x81"'.decode('utf-8')
    }
]

with open(csv_path, 'a', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=['File Path', 'Entry Name', 'Entry Index', 'English', 'Vietnamese'])
    writer.writerows(new_rows)
print("Done appending correctly.")
