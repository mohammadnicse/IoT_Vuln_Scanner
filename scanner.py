import os
import re
import sys
import json

# Define Patterns to Hunt
SECRET_PATTERNS = {
    "AWS_KEY": r"AKIA[0-9A-Z]{16}",
    "PRIVATE_KEY": r"-----BEGIN PRIVATE KEY-----",
    "HARDCODED_PASSWORD": r"password\s*=\s*['\"](.*)['\"]",
    "IP_ADDRESS": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
}

# Insecure C Functions
UNSAFE_FUNCTIONS = [
    b"strcpy",
    b"strcat",
    b"sprintf",
    b"system",
    b"gets"
]

def analyze_file(filepath):
    results = []
    try:
        # SKIP SPECIAL FILES
        if not os.path.isfile(filepath):
            return []

        with open(filepath, "rb") as f:
            content = f.read()

        # A. Binary Analysis
        if content.startswith(b"\x7fELF"):
            for func in UNSAFE_FUNCTIONS:
                if func in content:
                    results.append({
                        "type": "Insecure Function",
                        "match": func.decode('utf-8'),
                        "file": filepath
                    })
        
        # B. Text/Secret Analysis
        try:
            text_content = content.decode('utf-8', errors='ignore')
            for name, pattern in SECRET_PATTERNS.items():
                matches = re.findall(pattern, text_content)
                for match in matches:
                    results.append({
                        "type": "Potential Secret",
                        "description": name,
                        "match": match[:20] + "...", 
                        "file": filepath
                    })
        except Exception:
            pass 

    except Exception:
        pass
    
    return results

def main(directory):
    print(f"[*] Starting Python Analysis on: {directory}")
    vulnerabilities = []

    for root, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            # Skip symlinks
            if not os.path.islink(filepath):
                hits = analyze_file(filepath)
                if hits:
                    vulnerabilities.extend(hits)

    output_file = "scan_report.json"
    with open(output_file, "w") as f:
        json.dump(vulnerabilities, f, indent=4)
    
    print(f"[+] Analysis Complete. Found {len(vulnerabilities)} issues.")
    print(f"[+] Report saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scanner.py <extracted_folder_path>")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    main(target_dir)
