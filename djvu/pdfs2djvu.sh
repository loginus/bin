#!/bin/bash
for INPUT_FILE in "$@";
do
	pdf2djvu "$INPUT_FILE" -o "$INPUT_FILE.djvu"
done
