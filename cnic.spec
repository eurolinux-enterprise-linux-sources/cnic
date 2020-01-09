%define kmod_name		cnic
%define kmod_driver_version	2.5.9
%define kmod_rpm_release	1
%define kmod_git_hash		b7fab1d776e25e08af4a79d1976eedf94ef40ab0
%define kmod_kernel_version	2.6.32-220.el6
%define kmod_kbuild_dir		drivers/net/


%{!?dist: %define dist .el6}

Source0:	%{kmod_name}-%{kmod_driver_version}.tar.bz2			
Source1:	%{kmod_name}.files			
Source2:	%{kmod_name}.conf			
Source3:	find-requires.ksyms			
Source4:	find-provides.ksyms			
Source5:	kmodtool			
Source6:	symbols.greylist			
Source7:	cnic.preamble			

%define __find_requires %_sourcedir/find-requires.ksyms
%define __find_provides %_sourcedir/find-provides.ksyms %{kmod_name} %{?epoch:%{epoch}:}%{version}-%{release}

Name:		%{kmod_name}
Version:	%{kmod_driver_version}
Release:	%{kmod_rpm_release}%{?dist}
Summary:	%{kmod_name} kernel module

Group:		System/Kernel
License:	GPLv2
URL:		http://www.kernel.org/
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires:	%kernel_module_package_buildreqs
ExclusiveArch:  i686 x86_64


# Build only for standard kernel variant(s); for debug packages, append "debug"
# after "default" (separated by space)
%kernel_module_package -s %{SOURCE5} -f %{SOURCE1} -p %{SOURCE7} default

%description
%{kmod_name} - driver update

%prep
%setup
set -- *
mkdir source
mv "$@" source/
mkdir obj

%build
for flavor in %flavors_to_build; do
	rm -rf obj/$flavor
	cp -r source obj/$flavor

	# update symvers file if existing
	symvers=source/Module.symvers-%{_target_cpu}
	if [ -e $symvers ]; then
		cp $symvers obj/$flavor/%{kmod_kbuild_dir}/Module.symvers
	fi

	make -C %{kernel_source $flavor} M=$PWD/obj/$flavor/%{kmod_kbuild_dir} \
		NOSTDINC_FLAGS="-I $PWD/obj/$flavor/include"
done

if [ -d source/firmware ]; then
	make -C source/firmware
fi

%install
export INSTALL_MOD_PATH=$RPM_BUILD_ROOT
export INSTALL_MOD_DIR=extra/%{name}
for flavor in %flavors_to_build ; do
	make -C %{kernel_source $flavor} modules_install \
		M=$PWD/obj/$flavor/%{kmod_kbuild_dir}
	# Cleanup unnecessary kernel-generated module dependency files.
	find $INSTALL_MOD_PATH/lib/modules -iname 'modules.*' -exec rm {} \;
done

install -m 644 -D %{SOURCE2} $RPM_BUILD_ROOT/etc/depmod.d/%{kmod_name}.conf
install -m 644 -D %{SOURCE6} $RPM_BUILD_ROOT/usr/share/doc/kmod-%{kmod_name}/greylist.txt

if [ -d source/firmware ]; then
	make -C source/firmware INSTALL_PATH=$RPM_BUILD_ROOT INSTALL_DIR= install
fi

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Wed Apr 04 2012 Jiri Benc <jbenc@redhat.com> 2.5.9 1
- updated to new version

* Fri Jan 27 2012 Jiri Benc <jbenc@redhat.com> 2.5.7 8
- synced with 6.2 GA

* Fri Sep 30 2011 Jiri Olsa <jolsa@redhat.com> 2.5.7 6
- updated to new version

* Fri Sep 30 2011 unknown <unknown@localhost> 2.5.7 5
- updated to new version

* Thu Sep 22 2011 Jiri Benc <jbenc@redhat.com> 2.5.7 4
- build fix

* Tue Sep 20 2011 Jiri Benc <jbenc@redhat.com> 2.5.7 3
- build fix

* Tue Sep 20 2011 Jiri Benc <jbenc@redhat.com> 2.5.7 1
- updated to new version

* Fri Sep 16 2011 Jiri Benc <jbenc@redhat.com> 2.5.3 3
- testing revision

* Fri Aug 12 2011 Jiri Olsa <jolsa@redhat.com> 2.5.3 2
- added missing files cnic.conf, cnic.files

* Fri Aug 12 2011 Jiri Olsa <jolsa@redhat.com> 2.5.3 1
- zstream build changes

* Fri Jun 10 2011 Jiri Olsa <jolsa@redhat.com> 2.2.13 1
- cnic DUP module
