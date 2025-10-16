#!/bin/sh -e

CONFFILENAME=/sentinel/sentinel.conf
if [ ! -f $CONFFILENAME ]
then
    cp /tmp/sentinel.conf /sentinel/sentinel.conf
fi

set -- redis-sentinel "$@"

exec "$@"
