#!/bin/csh

#source activate dcm2bids

foreach subId(`seq -w 1 1 42`)

cd /Users/bernice/Documents/socialContext_BIDS
dcm2bids -d sourcedata/*SOCIAL_"$subId"_*/PSY*/ -p "$subId" -c code/socialContext_config.json

end
