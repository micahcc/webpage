#!/usr/bin/env bash
set -euo pipefail

nix-shell -p bundler --run "bundle install --gemfile=Gemfile --path vendor/cache"
nix-shell -p bundler --run "bundle exec jekyll serve"
