#!/bin/bash

KEEPFILES=$1

for file in *; do
    if ! grep -qxF "$file" "$KEEPFILES"; then
        echo "$file"
    fi
done

