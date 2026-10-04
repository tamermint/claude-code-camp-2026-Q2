#!/usr/bin/env bash

cd "$(dirname "$0")/../../ruby/04_api_client"
bundle install
bundle exec ruby examples/example.rb