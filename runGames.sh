#!/bin/bash

for i in {1..3000}
do
  num=$i*2
  ./halite -d "30 30" "python3 MyBot.py" "python3 OverkillBot.py" > tmp.log
  echo "Game $num" >> johnboronkas.log
  grep johnboronkas, tmp.log >> johnboronkas.log
  mv johnboronkas.log "$num.log"

  num=$i*3
  ./halite -d "30 30" "python3 MyBot.py" "python3 OverkillBot.py" "python3 OverkillBot.py" > tmp.log
  echo "Game $num" >> johnboronkas.log
  grep johnboronkas, tmp.log >> johnboronkas.log
  mv johnboronkas.log "$num.log"

  num=$i*4
  ./halite -d "30 30" "python3 MyBot.py" "python3 OverkillBot.py" "python3 OverkillBot.py" "python3 OverkillBot.py" > tmp.log
  echo "Game $num" >> johnboronkas.log
  grep johnboronkas, tmp.log >> johnboronkas.log
  mv johnboronkas.log "$num.log"
  rm tmp.log

  num=$i*5
  ./halite -d "30 30" "python3 MyBot.py" "python3 OverkillBot.py" "python3 OverkillBot.py" "python3 OverkillBot.py" "python3 OverkillBot.py" > tmp.log
  echo "Game $num" >> johnboronkas.log
  grep johnboronkas, tmp.log >> johnboronkas.log
  mv johnboronkas.log "$num.log"
  rm tmp.log

  num=$i*6
  ./halite -d "30 30" "python3 MyBot.py" "python3 OverkillBot.py" "python3 OverkillBot.py" "python3 OverkillBot.py" "python3 OverkillBot.py" "python3 OverkillBot.py" > tmp.log
  echo "Game $num" >> johnboronkas.log
  grep johnboronkas, tmp.log >> johnboronkas.log
  mv johnboronkas.log "$num.log"
  rm tmp.log

  ./resultSort.sh
  rm *.hlt
  rm *.log
done
