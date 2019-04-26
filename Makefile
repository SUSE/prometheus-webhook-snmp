# -*- mode: makefile; coding: utf-8 -*-
SHELL = /bin/bash
DOCDIR = /usr/share/doc/
VENVDIR = venv
PYTHON3_SITELIB = /usr/lib/python3/dist-packages
UNITDIR = /lib/systemd/system

mkvenv:
	( \
		virtualenv -p python3 $(VENVDIR); \
		. $(VENVDIR)/bin/activate; \
		pip install -r requirements.txt; \
	)

rmvenv:
	rm -rf $(VENVDIR)

test:
	tox

clean: rmvenv
	find . \( -name .tox -o -name .pytest_cache -o -name __pycache__ \) \
		-type d -print0 -prune | xargs -0r rm -rf
	rm -rf \
		debian/prometheus-webhook-snmp/ \
		debian/files \
		debian/.debhelper \
		debian/*.{log,substvars}

install:
	# Directories
	install -d -m 755 $(DESTDIR)/usr/bin/
	install -d -m 755 $(DESTDIR)$(PYTHON3_SITELIB)/prometheus_webhook_snmp/
	install -d -m 755 $(DESTDIR)$(DOCDIR)/prometheus-webhook-snmp/
	install -d -m 755 $(DESTDIR)$(UNITDIR)/
	# Files
	install -m 755 prometheus-webhook-snmp $(DESTDIR)/usr/bin/
	install -m 644 prometheus_webhook_snmp/*.py $(DESTDIR)$(PYTHON3_SITELIB)/prometheus_webhook_snmp/
	install -m 644 README.md $(DESTDIR)$(DOCDIR)/prometheus-webhook-snmp/
	install -m 644 prometheus-webhook-snmp.service $(DESTDIR)$(UNITDIR)/

.PHONY: mkvenv rmvenv test clean install
