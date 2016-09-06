
Name:           dciagent
Version:        0.0.VERS
Release:        1%{?dist}

Summary:        DCI agent
License:        ASL 2.0
URL:            https://github.com/Spredzy/agent2

Source0:        dciagent-%{version}.tgz

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-tox
BuildRequires:  python-requests
BuildRequires:  libffi-devel

Requires:       ansible
Requires:       python-click
Requires:       python-requests
Requires:       python-dciclient
Requires:       python-jinja2
Requires:       PyYAML


%description
DCI agent

%prep -a
%setup -qc

%build
%py2_build

%install
%py2_install


%check

%files
%doc
%{python2_sitelib}/*
%{_bindir}/dci-agent


%changelog
* Tue Sep 06 2016 Yanis Guenane <yguenane@redhat.com> 0.1-1
- Initial commit

