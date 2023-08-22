#!/bin/bash
rm build.zip
zip build img/ skymagic_atlas.png vanilla_atlas.png wiki -r
scp build.zip maluch.mikr.us:/var/www/skymagic/
ssh maluch.mikr.us "unzip -o /var/www/skymagic/build.zip -d /var/www/skymagic/"


