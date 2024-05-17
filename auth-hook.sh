#!/bin/bash

DOMAIN="_acme-challenge.$CERTBOT_DOMAIN"

VALUE="$CERTBOT_VALIDATION"

API_TOKEN="4753507255d86b08b1c2c2bd13fdb5362ab8241794c7373fe75d602cc9e39371"
DOMAIN_ID="2975758"

curl -X POST "https://api.linode.com/v4/domains/$DOMAIN_ID/records" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "TXT",
    "name": "'"$DOMAIN"'",
    "target": "'"$VALUE"'",
    "ttl_sec": 300
  }'
