#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml

with open("config.yml") as conf:
    data = yaml.load(conf)

print data
