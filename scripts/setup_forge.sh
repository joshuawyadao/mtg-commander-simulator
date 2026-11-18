#!/usr/bin/env bash
set -euo pipefail

destination=${1:?Usage: bash scripts/setup_forge.sh DESTINATION}
version=2.0.16
digest=feb1338c2f4a8c62e9289b6270caa7fcc38f2441d5ec4d7cff237c2c1a3b15d0
archive_url="https://github.com/Card-Forge/forge/releases/download/forge-$version/forge-installer-$version.tar.bz2"

mkdir -p -- "$destination"
archive=$(mktemp)
trap 'rm -f -- "$archive"' EXIT
curl --fail --location --silent --show-error --retry 3 --retry-max-time 180 \
    --connect-timeout 15 --max-time 120 --output "$archive" "$archive_url"
printf '%s  %s\n' "$digest" "$archive" | sha256sum --check --strict
tar -xjf "$archive" -C "$destination"

test -s "$destination/forge-gui-desktop-$version-jar-with-dependencies.jar"
test -s "$destination/res/cardsfolder/cardsfolder.zip"
printf 'Verified Forge %s archive (SHA-256 %s)\n' "$version" "$digest"
