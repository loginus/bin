#!/bin/bash
INPUT_FILE=$1;
tifftopnm "$INPUT_FILE" | cpaldjvu - "$INPUT_FILE".djvu
ls -l "$INPUT_FILE" "$INPUT_FILE".djvu
