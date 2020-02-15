#!/usr/bin/env bash

rm function.zip
cd env/lib/python3.7/site-packages/
zip -r ../../../../function.zip .
cd ../../../../
zip -g function.zip index.py
zip -g function.zip config.py
aws lambda update-function-code --function-name alexa-http-request --zip-file fileb://function.zip
