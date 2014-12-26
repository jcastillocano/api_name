#!/bin/bash
#===============================================================================
#
#          FILE:  apiname.sh
#
#         USAGE:  ./apiname.sh
#
#   DESCRIPTION:  API name.com bash script
#
#       OPTIONS:  $1 <username> $2 <token>
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Juan Carlos Castillo , juan.carlos@tuguu.com
#       COMPANY:  www.tuguu.com
#       VERSION:  1.0
#       CREATED:  21/12/14 23:06:35 WET
#      REVISION:  ---
#===============================================================================

URL='https://api.name.com'
LOGIN_DATA="{'username':'$1','api_token':'$2'}"
CIPHER='RC4-SHA'

# Login URL
TOKEN=`curl -X POST "$URL/api/login" --ciphers $CIPHER -d $LOGIN_DATA`
echo "Session token: ${TOKEN}"
# GET API status
HELLO=`curl -X GET "$URL/api/hello" --ciphers $CIPHER`
echo "Hello test: ${HELLO}"


