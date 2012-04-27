#The following python template strings will be filled in by invoking script.
%define name chatsvc
%define version 0.1
%define release 1

#Non-template defines
%define app_buildroot $RPM_BUILD_ROOT/%{__prefix}/%{name}-%{version}/%{name}
%define __prefix /opt/30and30/services/chatsvc/install
%define app_installroot %{__prefix}/%{name}-%{version}/%{name}

Summary: 30and30 Service 
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_topdir}/tmp/%{name}-%{version}-buildroot
Group: 30and30
Packager: 30and30
License: 30and30


%description 
Tech Residents Service

%prep
[ -d $RPM_BUILD_ROOT ] && rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{__prefix}
tar -C $RPM_BUILD_ROOT/%{__prefix} -xzf %{SOURCE0} 

%build
#virtualenv does do well with being create in long paths
#so we'll create it in RPM_BUILD_ROOT and relocate it 
#in the install section.
virtualenv --no-site-packages $RPM_BUILD_ROOT/env

%install
source $RPM_BUILD_ROOT/env/bin/activate
python %{app_buildroot}/bootstrap.py --requirements %{app_buildroot}/requirements/requirements.txt

# fix the #! line in installed python files
find "$RPM_BUILD_ROOT" -type f -print0 |
      xargs -0 egrep -l "/usr/local/bin/python|$RPM_BUILD_ROOT/.*/bin/python" | while read file
do
   FIXFILE="$file"
   sed 's|^#!.*python|#!%{app_installroot}/env/bin/python''|' \
         "$FIXFILE" >/tmp/fix-python-path.$
   cat /tmp/fix-python-path.$ >"$FIXFILE"
   rm -f /tmp/fix-python-path.$
done


#relocate virtualenv
virtualenv --relocatable $RPM_BUILD_ROOT/env
mv $RPM_BUILD_ROOT/env %{app_buildroot}/env

#fix activate scripts which --relocatable misses
find "%{app_buildroot}/env/bin" -name 'activate*' -type f -print0 |
      xargs -0 grep -l "$RPM_BUILD_ROOT" | while read file
do
   FIXFILE="$file"
   sed "s|$RPM_BUILD_ROOT|%{app_installroot}|" \
         "$FIXFILE" >/tmp/fix-virutalenv-path.$
   cat /tmp/fix-virutalenv-path.$ >"$FIXFILE"
   rm -f /tmp/fix-virtualenv-path.$
done

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, thirty, thirty)
/%{__prefix}/*

