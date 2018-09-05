#!usr/bin/env bash
ip="$1"
max="$2"
for (( i=1; i<=$max; i++ )); do
    bash -c "(</dev/tcp/$ip/$i) >/dev/null 2>&1" && echo -e "\nOpen:\t$i" || echo -ne "($((i-MINPORT))/$((max-1)))\r";
done

