#!/bin/bash

# Visual output colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}    Automated IoT Firmware Scanner       ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 1. Input Validation
if [ "$#" -ne 1 ]; then
    echo -e "${RED}[!] Usage: $0 <firmware_file.bin>${NC}"
    exit 1
fi

FIRMWARE=$1

if [ ! -f "$FIRMWARE" ]; then
    echo -e "${RED}[!] File not found!${NC}"
    exit 1
fi

# 2. Extraction Phase (Binwalk)
echo -e "${GREEN}[+] Target: $FIRMWARE${NC}"
echo -e "${GREEN}[+] Starting Firmware Extraction...${NC}"

# -e: extract, -M: recursively (matryoshka), --run-as=root (often needed for sqsh files)
binwalk -e -M "$FIRMWARE" --run-as=root

# Binwalk extracts to a folder named '_<filename>.extracted'
EXTRACTED_DIR="_$(basename "$FIRMWARE").extracted"

if [ -d "$EXTRACTED_DIR" ]; then
    echo -e "${GREEN}[+] Extraction Successful! Directory: $EXTRACTED_DIR${NC}"
else
    echo -e "${RED}[!] Extraction Failed. Check if binwalk is installed correctly.${NC}"
    exit 1
fi

# 3. Analysis Phase (Python)
echo -e "${GREEN}[+] Triggering Python Static Analysis...${NC}"
python3 scanner.py "$EXTRACTED_DIR"

# 4. Cleanup/Result Display
echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}[+] Scan Completed.${NC}"
echo -e "${GREEN}[+] Check scan_report.json for details.${NC}"
