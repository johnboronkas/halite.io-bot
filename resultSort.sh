#!/bin/bash

for file in *.log
do
  if grep "rank #1" $file
  then
    mv "$file" "wins/$file"
  fi
done
