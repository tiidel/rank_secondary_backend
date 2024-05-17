#!/bin/bash

DOMAIN="_acme-challenge.$CERTBOT_DOMAIN"

API_TOKEN="4753507255d86b08b1c2c2bd13fdb5362ab8241794c7373fe75d602cc9e39371"
DOMAIN_ID="2975758"

RECORD_ID=$(curl -s -X GET "https://api.linode.com/v4/domains/$DOMAIN_ID/records?type=TXT&name=$DOMAIN" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" | jq -r '.data[0].id')

curl -X DELETE "https://api.linode.com/v4/domains/$DOMAIN_ID/records/$RECORD_ID" \
  -H "Authorization: Bearer $API_TOKEN"
