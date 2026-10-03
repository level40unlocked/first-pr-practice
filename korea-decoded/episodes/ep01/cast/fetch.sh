#!/bin/sh
# Puppet source images (Higgsfield jobs listed in docs/show_bible.md). Not kept in git.
cd "$(dirname "$0")"
B=https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU
curl -sSf -o a_head.png $B/hf_20260928_074351_497d2899-66fc-40ea-8b60-1d4815c18eb6.png
curl -sSf -o a_body.png $B/hf_20260928_074350_480e7f2e-bde1-49fe-ad18-dfc5d2599626.png
curl -sSf -o a_ref.png  $B/hf_20260928_074351_5d746f9a-6b07-4adb-9eec-3936cf68fecf.png
curl -sSf -o p_head.png $B/hf_20260928_084541_c67fcd43-9c73-473c-b29f-4be8a1cd81e5.png
curl -sSf -o p_body.png $B/hf_20260928_084541_ec8bd826-58a3-4d75-bff3-18cce3c5a521.png
curl -sSf -o p_ref.png  $B/hf_20260928_084541_2a93c3aa-974e-40fb-b63a-26662d2f9796.png
