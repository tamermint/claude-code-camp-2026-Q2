#!/usr/bin/env bash

cd "$(dirname "$0")/../../ruby/03_prompt_builder"
bundle install
bundle exec ruby examples/example.rb