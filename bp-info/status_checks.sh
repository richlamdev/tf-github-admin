#!/bin/bash

echo "checking for required status checks"
#grep -A 10 '"required_status_checks":' ../branch-protection/*
grep -A2 '"checks": \[' ../branch-protection/*

