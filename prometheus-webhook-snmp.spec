#
# spec file for package prometheus-webhook-snmp
#
# Copyright (c) 2019-2020 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# bugs, issues, pull requests, please report via github.
# this software is a fork of github.com/SUSE/prometheus-webhook-snmp

Name:           prometheus-webhook-snmp
Version:        1.5
Release:        1
Summary:        Prometheus Alertmanager receiver for SNMP traps
License:        GPL-3.0
Url:            https://github.com/infrawatch/prometheus-webhook-snmp
Source0:        https://github.com/infrawatch/%{name}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-setuptools

%if 0%{?fedora}
BuildRequires:  python3-devel
BuildRequires:  systemd-rpm-macros
%endif

Requires:       python3-prometheus-client
Requires:       python3-click
%if 0%{?suse_version}
Requires:       python3-CherryPy
Requires:       python3-PyYAML
%else
Requires:       python3-cherrypy
Requires:       python3-yaml
%endif
Requires:       python3-dateutil
Requires:       python3-pysnmp >= 4.4.1

%description
prometheus-webhook-snmp is a Prometheus Alertmanager receiver that
translates incoming notifications into SNMP traps.

%prep
%setup -n %{name}-%{version}

%build

%install
make install DESTDIR=%{buildroot} PYTHON3_SITELIB=%{python3_sitelib} UNITDIR=%{_unitdir}

%pre
%systemd_pre %{name}.service

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%files
%doc README.md
%license LICENSE
%{_bindir}/%{name}
%{python3_sitelib}/prometheus_webhook_snmp
%{_unitdir}/%{name}.service

%changelog
* Mon Sep 14 2020 Matthias Runge <mrunge@redhat.com> - 1.5-1
- initial RPM packaging for Fedora/RHEL/CentOS
