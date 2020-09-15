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

# Please submit bugfixes or comments via http://bugs.opensuse.org/

Name:           prometheus-webhook-snmp
Version:        1.5
Release:        0
Summary:        Prometheus Alertmanager receiver for SNMP traps
License:        GPL-3.0
Group:          System/Management
Url:            https://github.com/SUSE/prometheus-webhook-snmp
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-setuptools

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
make install DESTDIR=%{buildroot} DOCDIR=%{_docdir} PYTHON3_SITELIB=%{python3_sitelib} UNITDIR=%{_unitdir}

%pre
%service_add_pre %{name}.service

%post
%service_add_post %{name}.service

%preun
%service_del_preun %{name}.service

%postun
%service_del_postun %{name}.service

%files
%doc README.md
%license LICENSE
%{_bindir}/%{name}
%dir %{python3_sitelib}/prometheus_webhook_snmp
%{python3_sitelib}/prometheus_webhook_snmp/__init__.py
%{python3_sitelib}/prometheus_webhook_snmp/utils.py
%{_unitdir}/%{name}.service

%changelog
