#!/bin/bash
wget "http://www.pkotfi.pl/index.php?id=csv&fundusz=FPA" -O /tmp/notow_modania.csv
awk -F ';' '{print $2" "$6" "$7" "$10}' /tmp/notow_modania.csv | sed -e "1s/^/% /" > /tmp/notowania.csv
