#!/bin/sh

PATH=/usr/bin:/bin

if [ -z "$1" ]; then
    echo "usage: $0 <version> <suffix>"
    exit 1
fi
name="$1"
if [ -n "$2" ]; then
    name="$1-$2"
fi

tmpd=/tmp/_boot_$name.backup
mkdir $tmpd

echo "Backing up /boot to $tmpd..."
cp -r /boot/* $tmpd/

current_initramfs=`find /boot -maxdepth 1 -type f |grep "\.img" |cut -d'/' -f3`
current_kernel=`find /boot -maxdepth 1 -type f |grep -v "$current_initramfs" |grep -v '\.keep' |cut -d'/' -f3`

echo "Replacing '$current_kernel' and '$current_initramfs'..."

find /boot -maxdepth 1 -type f |grep -v "\.keep" |xargs rm -f

echo "Kernel copy to '/boot/kernel-$name'"
cp /usr/src/linux/arch/x86_64/boot/bzImage /boot/kernel-$name


dra=`dracut --kernel-image /boot/kernel-$name -m "rootfs-block base" --no-kernel --force 2>&1 |grep "initramfs\(.*\)done" |cut -d'/' -f3 |cut -d"'" -f1`

if [ -n "$dra" ]; then
    mv "/boot/$dra" "/boot/initramfs-$name.img"
    echo "Initramfs 'initramfs-$name.img' installed"
else
    echo "Error@dracut"
    exit
fi

echo "Replacing grub entries.."
sed -i "s/$current_initramfs/initramfs-$name.img/g" /boot/grub/grub.cfg
sed -i "s/$current_kernel/kernel-$name/g" /boot/grub/grub.cfg
echo "grub entries replaced"
echo "should be good!"

