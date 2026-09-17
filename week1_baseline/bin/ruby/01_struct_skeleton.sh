#!/usr/bin/env bash

cd "$(dirname "$0")/../../ruby/01_struct_skeleton"
bundle install
bundle exec ruby examples/example.rb