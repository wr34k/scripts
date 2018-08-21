#!/bin/sh

if [ -z "$1" ]; then
    echo "Usage: $0 <binToJail>"
    exit
fi


BIN_PATH=`which "$1"`

if [ -z $BIN_PATH ]; then
    echo "$1 not found."
    exit
fi

echo "Jailing '$BIN_PATH'..."

JAIL=/opt/jails/$1


rm -rf $JAIL

# FS
mkdir $JAIL
mkdir $JAIL/{etc,dev,var,usr,run}

mkdir $JAIL/usr/share

mkdir $JAIL/lib64
mkdir $JAIL/usr/lib64

mkdir $JAIL/bin
mkdir $JAIL/usr/bin
mkdir $JAIL/usr/sbin

mkdir $JAIL/tmp
mkdir $JAIL/var/tmp

chmod 1777 $JAIL/tmp
chmod 1777 $JAIL/var/tmp

echo "Base filesystem created"

# dev

mknod -m 0666 $JAIL/dev/null c 1 3
mknod -m 0666 $JAIL/dev/random c 1 8
mknod -m 0444 $JAIL/dev/urandom c 1 9

echo "Special devices created"

# cp binary
cp "$BIN_PATH" "$JAIL$BIN_PATH"

echo "'$BIN_PATH' binary copied to '$JAIL$BIN_PATH'"

# required libs
RAW_LIBS=`ldd $BIN_PATH`

LIBS_LIST=`echo "$RAW_LIBS" |awk -F '=>' '{print $2}' |awk -F' ' '{print $1}'`

for lib in $LIBS_LIST; do
    echo "Copying '$lib' to '$JAIL$lib'..."
    cp "$lib" "$JAIL$lib"
done

cp /lib64/ld-linux-x86-64.so.2 $JAIL/lib64/

echo "Required libs copied"

# locales
echo "Copying locales..."
cp -r /usr/share/locale $JAIL/usr/share

# create passwd / group
grep "^nobody" /etc/passwd > $JAIL/etc/passwd
grep "^nobody" /etc/group > $JAIL/etc/group

# useful etc files
cp /etc/{resolv.conf,hosts,host.conf,nsswitch.conf} $JAIL/etc/

echo "Etc files created."

echo "Should be good to go!"
echo "start the chroot with 'chroot $JAIL $BIN_PATH'"
