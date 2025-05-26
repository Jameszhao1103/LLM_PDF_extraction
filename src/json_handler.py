import json
import pandas as pd
import os
import glob
import re


class JSONHandler:
    def save_to_json(self, data, filepath):
        with open(filepath, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=2, ensure_ascii=False)

    def load_from_json(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    
    def extract_json_from_content(self, content):
        """Extract JSON data from the content string that may contain markdown formatting"""
        try:
            # Remove markdown code block formatting
            if "```json" in content:
                # Extract content between ```json and ```
                json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Fallback: try to find JSON between any ``` blocks
                    json_match = re.search(r'```\s*\n(.*?)\n```', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                    else:
                        json_str = content
            else:
                json_str = content
            
            # Parse the JSON
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
    
    def convert_outputs_to_excel(self, output_dir="../data/output", excel_filename="extracted_data.xlsx"):
        """Convert all JSON output files to Excel format"""
        # Find all JSON output files
        json_pattern = os.path.join(output_dir, "*_output.json")
        json_files = glob.glob(json_pattern)
        
        if not json_files:
            print(f"No output JSON files found in {output_dir}")
            return False
        
        print(f"Found {len(json_files)} JSON files to convert")
        
        # List to store all extracted data
        all_data = []
        
        for json_file in json_files:
            try:
                # Load the JSON file
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract the filename for reference
                filename = os.path.basename(json_file).replace('_output.json', '')
                
                # Check if processing was successful
                if data.get("success", False):
                    content = data.get("content", "")
                    
                    # Extract JSON from content
                    extracted_json = self.extract_json_from_content(content)
                    
                    if extracted_json:
                        # Add filename for reference
                        extracted_json["源文件名"] = filename
                        all_data.append(extracted_json)
                        print(f"✅ Processed: {filename}")
                    else:
                        print(f"❌ Failed to extract JSON from: {filename}")
                else:
                    print(f"❌ Processing failed for: {filename} - {data.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Error processing {json_file}: {str(e)}")
        
        if not all_data:
            print("No valid data found to convert to Excel")
            return False
        
        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        
        # Reorder columns to put filename first
        if "源文件名" in df.columns:
            cols = ["源文件名"] + [col for col in df.columns if col != "源文件名"]
            df = df[cols]
        
        # Save to Excel
        excel_path = os.path.join(output_dir, excel_filename)
        df.to_excel(excel_path, index=False, engine='openpyxl')
        
        print(f"\n✅ Successfully converted {len(all_data)} records to Excel")
        print(f"📊 Excel file saved to: {excel_path}")
        print(f"📋 Columns: {list(df.columns)}")
        
        return True
    
    def preview_extracted_data(self, output_dir="../data/output", num_samples=3):
        """Preview some extracted data to verify the conversion"""
        json_pattern = os.path.join(output_dir, "*_output.json")
        json_files = glob.glob(json_pattern)[:num_samples]
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                filename = os.path.basename(json_file)
                print(f"\n📄 File: {filename}")
                print("-" * 50)
                
                if data.get("success", False):
                    content = data.get("content", "")
                    extracted_json = self.extract_json_from_content(content)
                    
                    if extracted_json:
                        for key, value in extracted_json.items():
                            print(f"{key}: {value}")
                    else:
                        print("Failed to extract JSON")
                else:
                    print(f"Processing failed: {data.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"Error: {str(e)}")