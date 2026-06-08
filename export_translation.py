import os
import json
import csv

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    extracted_dir = os.path.join(script_dir, "extracted_msg")
    output_csv = os.path.join(script_dir, "vietnamese_translation.csv")

    total_files = 0
    total_entries = 0
    valid_entries = 0
    rows = []

    for root, dirs, files in os.walk(extracted_dir):
        for f_name in files:
            if f_name.endswith(".json"):
                total_files += 1
                full_path = os.path.join(root, f_name)
                
                rel_path = os.path.relpath(full_path, extracted_dir)
                if rel_path.endswith(".json"):
                    rel_path = rel_path[:-5]
                
                with open(full_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except Exception as e:
                        print(f"Error loading {full_path}: {e}")
                        continue
                    
                    entries = data.get("entries", [])
                    for idx, entry in enumerate(entries):
                        total_entries += 1
                        name = entry.get("name", "")
                        content = entry.get("content", [])
                        
                        if len(content) > 1:
                            english_text = content[1]
                            
                            # Filter out empty or placeholders like <END>
                            if english_text.strip() and english_text.strip() != "<END>":
                                valid_entries += 1
                                rows.append({
                                    "File Path": rel_path,
                                    "Entry Name": name,
                                    "Entry Index": idx,
                                    "English": english_text,
                                    "Vietnamese": ""
                                })

    # Write to CSV
    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["File Path", "Entry Name", "Entry Index", "English", "Vietnamese"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Scanned {total_files} JSON files.")
    print(f"Total entries: {total_entries}")
    print(f"Valid English entries exported to CSV: {valid_entries}")
    print(f"CSV saved to: {output_csv}")

if __name__ == "__main__":
    main()
