#!/bin/bash

echo "checking for enforce_admins"
grep '"enforce_admins": false' ../branch-protection/*

echo "number of matches enforce_admins: false"
grep '"enforce_admins": false' ../branch-protection/* | wc -l
