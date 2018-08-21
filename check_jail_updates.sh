#!/bin/sh

BASE=/opt/jails

OMIT=/etc:tor/data/state:.pid:access_log:error_log

if [ -z "$1" ]; then
    JAILS=`ls -d $BASE/*/`
else
    JAILS="$1"
fi

echo "[*] Omitting these patterns in filenames: '$OMIT'"

for i in $JAILS; do

    echo "[*] Now checking '$i' ..."
    JAIL_OUTDATED=false

    JAIL_FILES=`find "$i" -type f`

    for file in $JAIL_FILES; do

        OLD_IFS=$IFS
        IFS=":" read -ra OMIT_PATTERNS <<< "$OMIT"
        skip=false
        for j in ${OMIT_PATTERNS[@]}; do
            if [[ "$file" =~ $j ]]; then
                skip=true
                continue
            fi
        done

        if $skip; then
            # echo "Skipping '$file'..."
            continue
        fi

        original_file="/${file/${i:-1}/}"
        #original_file=$(echo "$file" |sed -e "s~$i~~g")
        if [ ! -f "$original_file" ]; then
            continue
        fi
        if [ "$(md5sum "$original_file" |cut -d' ' -f1)" != "$(md5sum "$file" |cut -d' ' -f1)" ]; then
            echo "[!] '$file' is outdated"
            JAIL_OUTDATED=true
        fi

    done

    if $JAIL_OUTDATED; then
        echo "[!] Jail is outdated, TODO: code the automatic copy."
    else
        echo "[*] All good!"
    fi

done
