import csv

csv_path = r'd:\RE4_VietHoa\vietnamese_translation.csv'

new_rows = [
    {
        "File Path": r"natives\stm\_chainsaw\message\mes_main_sys\ch_mes_main_sys_tutorial.msg.22",
        "Entry Name": "CH_Mes_Main_Sys_TutorialBody_005",
        "Entry Index": "11",
        "English": "<ICON CROUCH> Crouch / Stand",
        "Vietnamese": "<ICON CROUCH> Ngồi / Đứng"
    },
    {
        "File Path": r"natives\stm\_chainsaw\message\mes_main_file\ch_mes_main_file_038.msg.22",
        "Entry Name": "CH_Mes_Main_File_038_00",
        "Entry Index": "0",
        "English": "Crude Charm",
        "Vietnamese": "Bùa thô"
    },
    {
        "File Path": r"natives\stm\_chainsaw\message\mes_main_file\ch_mes_main_file_038.msg.22",
        "Entry Name": "CH_Mes_Main_File_038_01",
        "Entry Index": "1",
        "English": "\"Judgment is Nigh\"",
        "Vietnamese": "\"Sự phán xét đã cận kề\""
    }
]

with open(csv_path, 'a', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=["File Path", "Entry Name", "Entry Index", "English", "Vietnamese"])
    writer.writerows(new_rows)

print("Appended missing entries to CSV.")
