#!/usr/bin/env python

import os,sys,common
import fetch_corpus

def main():
  print "Fetching corpus."
  fetch_corpus.fetch_corpus()

  print "Fetching dependencies"
  common.run_cmd(['bash', 'fetch_dependencies.sh'])

if __name__ == "__main__":
  main()
