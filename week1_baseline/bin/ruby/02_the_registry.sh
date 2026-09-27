#!/usr/bin/env bash

cd "$(dirname "$0")/../../ruby/02_the_registry"
bundle install
bundle exec ruby examples/example.rb