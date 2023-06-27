#!/bin/bash

echo "checking for required_approving_review_count"
grep '"required_approving_review_count":' ../branch-protection/*

echo "number of matches:"
grep '"required_approving_review_count":' ../branch-protection/* | wc -l
