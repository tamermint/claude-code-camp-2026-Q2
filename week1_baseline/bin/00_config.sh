#!/usr/bin/env bash

cd "$(dirname "$0")/../ruby/00_config"
bundle install
bundle exec ruby examples/example.rb