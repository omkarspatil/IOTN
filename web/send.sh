#!/bin/bash
 
# This needs heirloom-mailx
from="dr.prerana@omkarpatil.info"
to=$1
bcc=$2
subject=$3
body=$4
declare -a attachments
attachments=( $5 $6 )
echo "Here"
declare -a attargs
for att in "${attachments[@]}"; do
  attargs+=( "-a"  "$att" )  
done
 
mail -b "$bcc" -s "$subject" -r "$from" "${attargs[@]}" "$to" <<< "$body"
echo "Done"
