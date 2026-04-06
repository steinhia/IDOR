#!/bin/bash
# Script to rename Zotero BibTeX keys to AuthorYear format
# Only capitalizes the first letter of the author name
# Keeps all entry content intact
# Works for @article, @book, @incollection, @misc

INPUT_FILE="PRONAS.bib"
OUTPUT_FILE="PRONAS_clean.bib"

awk '
BEGIN {
    # Allowed BibTeX types
    entry_types["@article"]=1
    entry_types["@book"]=1
    entry_types["@incollection"]=1
    entry_types["@misc"]=1
}

/^@/ {
    # Detect start of entry
    split($0, parts, /[ \t{]/)
    type = parts[1]
    if(type in entry_types){
        # Extract everything between { and first comma as key
        start = index($0, "{")
        end = index($0, ",")
        if(start > 0 && end > start){
            original_key = substr($0, start+1, end-start-1)

            # Split key by underscore
            n = split(original_key, key_parts, "_")
            author = key_parts[1]
            year = key_parts[n]

            # Remove non-letter characters from author
            gsub(/[^a-zA-Z]/,"",author)

            # Capitalize first letter only
            if(length(author) > 0){
                author = toupper(substr(author,1,1)) tolower(substr(author,2))
            }

            # Compose new key
            new_key = author year

            # Print modified entry start
            print type "{" new_key ","
            next
        }
    }
}
{
    # Print all other lines as is
    print
}
' "$INPUT_FILE" > "$OUTPUT_FILE"

echo "Finished renaming keys in $OUTPUT_FILE"
