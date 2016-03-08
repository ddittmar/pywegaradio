#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
# logging.basicConfig()

log = logging.getLogger('daemon.py')
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s (%(name)s) [%(levelname)s] - %(message)s'))
log.addHandler(handler)

log.debug("test?")
log.info("test?")
log.warn("test?")
log.error("test?")
