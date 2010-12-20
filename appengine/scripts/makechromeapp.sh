#! /bin/sh
# Package up a thin wrapper of icons and guff for uploading to the Chrome web store.

PACKAGELOC=/tmp/astrozac.zip
BUILDLOC=$(mktemp -d /tmp/appXXXX)
rm -rf $PACKAGELOC
cp chromeapp/manifest.json static/app-icon*.png $BUILDLOC
cd $BUILDLOC
zip $PACKAGELOC *

echo "Packaged app is $PACKAGELOC"