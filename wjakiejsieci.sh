#!/bin/bash
NUMBER="$1"
OPERATOR_SEC=$(curl -s 'http://www.wjakiejsieci.pl/' --data "prefix=%2B48&phone=$NUMBER&kod67d8651888=78a042c93eaae82b81d41dc1198e1e716b679cba961b3edad4ab93de967d8ee2&dziady=jedne" | grep 'class="operator"')
OPERATOR=$(echo $OPERATOR_SEC | sed -s "s/^.*<strong>\(.\+\)<\/strong>.*/\1/")
echo $OPERATOR
