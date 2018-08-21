#!/bin/sh

for i in `seq 1 $1`; do
    ip=2001:41d0:1:569f::$(( (RANDOM % 9000) + 1 )):$(( (RANDOM % 9000) + 1 ))
    echo "Adding $ip ..."

    ip -6 addr add $ip dev eth0

done
