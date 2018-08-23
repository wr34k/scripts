#!/usr/bin/env bash

ls $HOME/wallpapers/ |sort -R |tail -1 |while read file; do

    feh --bg-center "$HOME/wallpapers/$file"
    wal -i "$HOME/wallpapers/$file"

done
