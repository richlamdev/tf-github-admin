#!/bin/bash

echo "checking for required status checks"
#grep -A 10 '"required_status_checks":' ../branch-protection/*
grep '"checks": \[\]' ../branch-protection/*

echo
echo "number of repos without status checks:"
grep '"checks": \[\]' ../branch-protection/* | wc -l
