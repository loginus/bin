#!/bin/bash
INPUT_FILE=$1;
giftopnm "$INPUT_FILE" | cpaldjvu - "$INPUT_FILE".djvu
ls -l "$INPUT_FILE" "$INPUT_FILE".djvu
