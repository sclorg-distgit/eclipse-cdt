%{?scl:%scl_package eclipse-cdt}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

%global baserelease 3

%global debug_package %{nil}
%global _enable_debug_packages 0
%global __jar_repack %{nil}

%if 0%{?fedora} >= 24
%global droplets droplets
%else
%global droplets dropins
%endif

# Change following to 0 to default to no container/remote support when building for 
# first time in a release...this is needed to build eclipse-linuxtools-docker and
# eclipse.remote which are circular dependencies of eclipse-cdt
%global _enable_container_and_remote_support 1

Epoch: 1

%global major                   8
%global minor                   8
%global majmin                  %{major}.%{minor}
%global micro                   1
%global eclipse_base            %{_libdir}/eclipse
%global cdt_snapshot            org.eclipse.cdt-CDT_8_8_1

# All arches line up except i386 -> x86
%ifarch %{ix86}
%global eclipse_arch    x86
%else
%ifarch %{arm}
%global eclipse_arch    arm
%else
%global eclipse_arch    %{_arch}
%endif
%endif

Summary:        Eclipse C/C++ Development Tools (CDT) plugin
Name:           %{?scl_prefix}eclipse-cdt
Version:        %{majmin}.%{micro}
Release:        9.%{baserelease}%{?dist}
License:        EPL and CPL
URL:            http://www.eclipse.org/cdt

Source0: http://git.eclipse.org/c/cdt/org.eclipse.cdt.git/snapshot/%{cdt_snapshot}.tar.xz

Source3: eclipse-cdt.desktop

# man-page for /usr/bin/cdtdebug
Source4: cdtdebug.man

# Script to run the tests in Xvnc
Source5: %{pkg_name}-runtests.sh

# Following adds current directory to autotools tests build.properties
Patch0: %{pkg_name}-autotools-test.patch

# Following fixes cdtdebug.sh script to get proper platform filesystem plugin
Patch1: %{pkg_name}-cdtdebug.patch

# Following fixes Standalone Debugger config.ini file to use bundle symbolic names
Patch2: %{pkg_name}-config-ini.patch

# Following fixes Standalone Debugger README file to refer to /usr/bin/cdtdebug
Patch3: %{pkg_name}-cdtdebug-readme.patch

# Following removes docker launcher plugins from repo
Patch4: remove-docker.patch

# Following removes autotools and remote plugins from repo
Patch5: remove-remote.patch

# Adds missing test resources
Patch6: eclipse-cdt-debug-app-tests.patch

# Fix Connection setting in C/C++ Docker Launch configuration
Patch7: eclipse-cdt-docker-launch-config.patch

BuildRequires: %{?scl_prefix}tycho
BuildRequires: %{?scl_prefix}tycho-extras
BuildRequires: %{?scl_prefix}eclipse-license
BuildRequires: desktop-file-utils
BuildRequires: %{?scl_prefix}lpg-java-compat
BuildRequires: %{?scl_prefix_java_common}google-gson
BuildRequires: %{?scl_prefix}eclipse-platform
BuildRequires: %{?scl_prefix}eclipse-contributor-tools
BuildRequires: %{?scl_prefix}eclipse-swtbot
BuildRequires: %{?scl_prefix_maven}exec-maven-plugin
%if %{_enable_container_and_remote_support}
BuildRequires: %{?scl_prefix}eclipse-linuxtools-docker
BuildRequires: %{?scl_prefix}eclipse-remote >= 2.0.0-1
BuildRequires: %{?scl_prefix}eclipse-rse
%endif

Requires:      %{?scl_prefix}gdb make %{?scl_prefix}gcc-c++
%if %{_enable_container_and_remote_support}
Requires:      autoconf automake libtool
Requires:      %{?scl_prefix}eclipse-remote >= 2.0.0-1
%endif

%description
Eclipse features and plugins that are useful for C and C++ development.

%package parsers
Summary:        Eclipse C/C++ Development Tools (CDT) Optional Parsers
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       %{?scl_prefix}lpg-java-compat

%description parsers
Optional language-variant parsers for the CDT.

%if %{_enable_container_and_remote_support} == 1

%package docker
Summary:        C/C++ Docker Launcher
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       %{?scl_prefix}eclipse-linuxtools-docker

%description docker
Special launcher for CDT to allow launching and debugging C/C++ applications
in Docker Containers.

%endif

%package qt
Summary:        QT C++ Tools
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description qt
Extensions to support Qt projects and objects in the indexer.

%package tests
Summary:        Eclipse C/C++ Development Tools (CDT) Tests
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       %{name}-parsers = %{epoch}:%{version}-%{release}
Requires:       %{?scl_prefix}eclipse-tests

%description tests
Test plugins for the CDT.

%package sdk
Summary:        Eclipse C/C++ Development Tools (CDT) SDK plugin
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description sdk
Source for Eclipse CDT for use within Eclipse.

%prep
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%setup -q -n %{cdt_snapshot}

# get desktop info
mkdir desktop
cp %{SOURCE3} desktop

# handle man page
mkdir man
cp %{SOURCE4} man

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch7 -p1
%if %{_enable_container_and_remote_support} == 0
%patch4 -p0
%patch5 -p0
%else
# Docker not available on F22 or earlier
%if 0%{?fedora} == 22
%patch4 -p0
%endif
%endif
%patch6 -p0

TYCHO_ENV="<environment><os>linux</os><ws>gtk</ws><arch>%{eclipse_arch}</arch></environment>"
%pom_xpath_set "pom:configuration/pom:environments" "$TYCHO_ENV"
%pom_xpath_set "pom:configuration/pom:environments" "$TYCHO_ENV" core/org.eclipse.cdt.core.linux

# Add secondary arch support if we are building there
%ifarch %{arm} s390 s390x aarch64
pushd core
pushd org.eclipse.cdt.core.native
sed -i -e 's/linux.x86 /linux.%{eclipse_arch} /g' plugin.properties
sed -i -e 's/\\(x86\\)/(%{eclipse_arch})/g' plugin.properties
popd
cp -r org.eclipse.cdt.core.linux.x86 org.eclipse.cdt.core.linux.%{eclipse_arch}
rm -fr org.eclipse.cdt.core.linux.x86
pushd org.eclipse.cdt.core.linux.%{eclipse_arch}
sed -i -e 's/x86/%{eclipse_arch}/g' pom.xml
sed -i -e 's/x86/%{eclipse_arch}/g' META-INF/MANIFEST.MF
mv os/linux/x86 os/linux/%{eclipse_arch}
popd
popd
pushd releng/org.eclipse.cdt.native-feature
sed -i -e 's/"org.eclipse.cdt.core.linux.x86"/"org.eclipse.cdt.core.linux.%{eclipse_arch}"/g' feature.xml
sed -i -e 's/arch="x86"/arch="%{eclipse_arch}"/' feature.xml
popd
sed -i -e "s|org.eclipse.cdt.core.linux.x86</module>|org.eclipse.cdt.core.linux.%{eclipse_arch}</module>|g" pom.xml
%endif
# Force the linux arch-specific plug-in to be a dir so that the .so files aren't loaded into
# the user.home .eclipse configuration
pushd core/org.eclipse.cdt.core.linux.%{eclipse_arch}
sed -i -e"/Bundle-Localization: plugin/ aEclipse-BundleShape: dir" META-INF/MANIFEST.MF
popd

# Don't use the target configuration
%pom_disable_module releng/org.eclipse.cdt.target
%pom_xpath_remove "pom:configuration/pom:target"

# Don't need to build the repo
%pom_disable_module releng/org.eclipse.cdt.repo

# Disable the jgit provider and force default packaging
%pom_remove_plugin org.eclipse.tycho:tycho-packaging-plugin
%pom_remove_plugin org.jacoco:jacoco-maven-plugin

# Disable docker, autotools, and remote features if we are building a boot-strap build
%if %{_enable_container_and_remote_support} == 0
%pom_disable_module launch/org.eclipse.cdt.docker.launcher
%pom_disable_module launch/org.eclipse.cdt.docker.launcher-feature
%pom_disable_module launch/org.eclipse.cdt.docker.launcher.source-feature
%pom_disable_module build/org.eclipse.cdt.autotools.core
%pom_disable_module build/org.eclipse.cdt.autotools.ui
%pom_disable_module build/org.eclipse.cdt.autotools.docs
%pom_disable_module build/org.eclipse.cdt.autotools.tests
%pom_disable_module build/org.eclipse.cdt.autotools.ui.tests
%pom_disable_module build/org.eclipse.cdt.autotools-feature
%pom_disable_module build/org.eclipse.cdt.autotools.source-feature
%pom_disable_module build/org.eclipse.linuxtools.cdt.autotools.core
%pom_disable_module cross/org.eclipse.cdt.launch.remote
%pom_disable_module cross/org.eclipse.cdt.launch.remote-feature
%pom_disable_module remote/org.eclipse.cdt.remote.core
%pom_disable_module remote/org.eclipse.cdt.remote-feature
%else
# Docker not available on F22 or earlier
%if 0%{?fedora} == 22
%pom_disable_module launch/org.eclipse.cdt.docker.launcher
%pom_disable_module launch/org.eclipse.cdt.docker.launcher-feature
%pom_disable_module launch/org.eclipse.cdt.docker.launcher.source-feature
%endif
%endif

# Remove arduino, llvm and p2 installer
%pom_disable_module toolchains/arduino/org.eclipse.cdt.arduino.core
%pom_disable_module toolchains/arduino/org.eclipse.cdt.arduino.ui
%pom_disable_module toolchains/arduino/org.eclipse.cdt.arduino-feature
%pom_disable_module llvm/org.eclipse.cdt.managedbuilder.llvm.ui
%pom_disable_module llvm/org.eclipse.cdt.managedbuilder.llvm-feature
%pom_disable_module p2/org.eclipse.cdt.p2
%pom_disable_module p2/org.eclipse.cdt.p2-feature

for b in `ls core/ | grep -P -e 'org.eclipse.cdt.core\.(?!linux\.%{eclipse_arch}$|tests$|linux$|native$)'` ; do
  module=$(grep ">core/$b<" pom.xml || :)
  if [ -n "$module" ] ; then
    %pom_disable_module core/$b
    %pom_xpath_remove "plugin[@id='$b']" releng/org.eclipse.cdt.native-feature/feature.xml
  fi
done
for b in aix macosx solaris win32 ; do
  %pom_xpath_remove "plugin[@id='org.eclipse.cdt.core.$b.source']" releng/org.eclipse.cdt.native.source-feature/feature.xml
done

# Add explicit dep on hamcrest for tests
sed -i -e "s|org.junit|org.hamcrest.core, org.junit|g" dsf-gdb/org.eclipse.cdt.tests.dsf.gdb/META-INF/MANIFEST.MF

# Drop unnecessary dep on log4j
sed -i -e '/log4j/d' build/org.eclipse.cdt.autotools.ui.tests/META-INF/MANIFEST.MF

%mvn_package "::pom::" __noinstall
%mvn_package ::jar:sources: sdk
%mvn_package ":*.source{,.feature}" sdk
%mvn_package :*.sdk sdk
%mvn_package :*.doc.isv sdk
%mvn_package ":*.testsrunner.test" tests
%mvn_package ":*.testsrunner*"
%mvn_package ":*.test{,s}*" tests
%mvn_package :*parser* parsers
%mvn_package ":org.eclipse.cdt.*{xlc,xlupc,bupc}*" parsers
%mvn_package :org.eclipse.cdt.docker* docker
%mvn_package :org.eclipse.cdt.qt* qt
%mvn_package :org.eclipse.cdt*
%{?scl:EOF}


%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
export JAVA_HOME=/usr/lib/jvm/java-1.8.0

# Exclude EquinoxResolver to avoid NPE occuring on arm
%ifarch %{arm}
export MAVEN_OPTS="-XX:CompileCommand=exclude,org/eclipse/tycho/core/osgitools/EquinoxResolver,newState"
%endif

pushd core/org.eclipse.cdt.core.linux/library
make JAVA_HOME="$JAVA_HOME" ARCH=%{eclipse_arch} CC='gcc -D_GNU_SOURCE'
popd

%mvn_build -j -f -- -Dtycho.local.keepTarget -Dskip-ppc64le
%{?scl:EOF}


%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%mvn_install

binInstallDir=${RPM_BUILD_ROOT}/%{_bindir}
manInstallDir=${RPM_BUILD_ROOT}/%{_mandir}/man1
install -d -m755 $binInstallDir
install -d -m755 $manInstallDir

cat << EOFSCRIPT > eclipse-runCDTTestBundles
#! /bin/bash
eclipse-runTestBundles %{_javadir}/cdt-tests
EOFSCRIPT

install -D -m 755 eclipse-runCDTTestBundles %{buildroot}%{_bindir}/eclipse-runCDTTestBundles

pushd %{buildroot}%{eclipse_base}/%{droplets}/cdt/eclipse/plugins
DEBUGAPPLICATIONVERSION=$(ls . | grep org.eclipse.cdt.debug.application_ | sed 's/org.eclipse.cdt.debug.application_//' |sed 's/.jar//')
pushd org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION
# Create the jar file inside the folder to work around issue where standalone application cannot be found without a jar file
jar -cfmv org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION.jar META-INF/MANIFEST.MF *
popd

# Fix the cdtdebug.sh script to hard-code ECLIPSE_HOME and cdt droplets directory
sed -i -e "s,@ECLIPSE_HOME@,%{eclipse_base}," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/cdtdebug.sh
sed -i -e "s,@CDT_DROPINS@,%{eclipse_base}/%{droplets}/cdt/eclipse/plugins," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/cdtdebug.sh
# Fix the dropin bundles to have full paths to their respective jar files as Eclipse start-up won't find them otherwise

for PLUGIN in \
$(ls . | grep org.eclipse.cdt.core.linux_) \
$(ls . | grep org.eclipse.cdt.core_) \
$(ls . | grep org.eclipse.cdt.debug.ui.memory.floatingpoint_) \
$(ls . | grep org.eclipse.cdt.make.core_) \
$(ls . | grep org.eclipse.cdt.dsf.ui_) \
$(ls . | grep org.eclipse.cdt.debug.ui.memory.traditional_) \
$(ls . | grep org.eclipse.cdt.ui_) \
$(ls . | grep org.eclipse.cdt.core_) \
$(ls . | grep org.eclipse.cdt.debug.application.doc_) \
$(ls . | grep org.eclipse.cdt.dsf.gdb.ui_) \
$(ls . | grep org.eclipse.cdt.debug.mi.ui_) \
$(ls . | grep org.eclipse.cdt.launch_) \
$(ls . | grep org.eclipse.cdt.managedbuilder.core_) \
$(ls . | grep org.eclipse.cdt.managedbuilder.gnu.ui_) \
$(ls . | grep org.eclipse.cdt.gdb_) \
$(ls . | grep org.eclipse.cdt.dsf.gdb_) \
$(ls . | grep org.eclipse.cdt.dsf_) \
$(ls . | grep org.eclipse.cdt.debug.mi.core_) \
$(ls . | grep org.eclipse.cdt.gdb.ui_) \
$(ls . | grep org.eclipse.cdt.debug.ui.memory.transport_) \
$(ls . | grep org.eclipse.cdt.debug.ui.memory.search_) \
$(ls . | grep org.eclipse.cdt.debug.ui.memory.memorybrowser_) \
$(ls . | grep org.eclipse.cdt.debug.ui_) \
$(ls . | grep org.eclipse.cdt.debug.core_) \
$(ls . | grep org.eclipse.cdt.core.native_) \
$(ls . | grep 'org.eclipse.cdt.core.linux\..*' | grep -v source);
do
  sed -i -e "s,${PLUGIN%_*}\,,file\\\\:%{eclipse_base}/%{droplets}/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
done

sed -i -e "s,org.eclipse.cdt.debug.application\,,file\\\\:%{eclipse_base}/%{droplets}/cdt/eclipse/plugins/org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION.jar\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini

sed -i -e "s,cp config.ini,cp %{eclipse_base}/%{droplets}/cdt/eclipse/plugins/org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/cdtdebug.sh
sed -i -e "s,cp dev.properties,cp %{eclipse_base}/%{droplets}/cdt/eclipse/plugins/org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/dev.properties," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/cdtdebug.sh
install -D -m 755 org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/cdtdebug.sh $binInstallDir/cdtdebug
popd

echo %{eclipse_base}/%{droplets}/cdt/eclipse/plugins/org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION.jar >> .mfiles

%{?scl: sed -i -e 's/Exec=cdtdebug/Exec=scl enable %{scl_name} cdtdebug/g' desktop/eclipse-cdt.desktop}
%{?scl: sed -i -e 's/Icon=eclipse/Icon=%{?scl_prefix}eclipse/g' desktop/eclipse-cdt.desktop}
%{?scl: sed -i -e 's,Name=Eclipse C/C++ Debugger,Name=DTS Eclipse C/C++ Debugger,g' desktop/eclipse-cdt.desktop}
install -D desktop/eclipse-cdt.desktop $RPM_BUILD_ROOT/usr/share/applications/%{name}.desktop
desktop-file-validate $RPM_BUILD_ROOT/usr/share/applications/%{name}.desktop

# man page
cp man/cdtdebug.man $manInstallDir/cdtdebug.1
%{?scl:EOF}


%files -f .mfiles
%{_bindir}/cdtdebug
/usr/share/applications/*
%{_mandir}/man1/cdtdebug.1*
%doc releng/org.eclipse.cdt.releng/epl-v10.html
%doc releng/org.eclipse.cdt.releng/notice.html

%files sdk -f .mfiles-sdk
%doc releng/org.eclipse.cdt.releng/epl-v10.html
%doc releng/org.eclipse.cdt.releng/notice.html

%files parsers -f .mfiles-parsers
%doc releng/org.eclipse.cdt.releng/epl-v10.html
%doc releng/org.eclipse.cdt.releng/notice.html

%files tests -f .mfiles-tests
%{_bindir}/eclipse-runCDTTestBundles
%doc releng/org.eclipse.cdt.releng/epl-v10.html
%doc releng/org.eclipse.cdt.releng/notice.html

%files qt -f .mfiles-qt
%doc releng/org.eclipse.cdt.releng/epl-v10.html
%doc releng/org.eclipse.cdt.releng/notice.html

%if %{_enable_container_and_remote_support} == 1

%files docker -f .mfiles-docker
%doc releng/org.eclipse.cdt.releng/epl-v10.html
%doc releng/org.eclipse.cdt.releng/notice.html
%endif

%changelog
* Wed Apr 06 2016 Jeff Johnston <jjohnstnm@redhat.com> - 1:8.8.1-9.3
- Fix Connection setting in C/C++ Docker launch configuration
- Resolves: #rhbz1279800

* Thu Mar 31 2016 Mat Booth <mat.booth@redhat.com> - 1:8.8.1-9.2
- Fix missing resources for debug app tests

* Tue Mar 29 2016 Mat Booth <mat.booth@redhat.com> - 1:8.8.1-9.1
- Import latest from Fedora

* Thu Mar 10 2016 Mat Booth <mat.booth@redhat.com> - 1:8.8.1-9
- Make standalone debugger work with all versions of lucene

* Thu Mar 10 2016 Mat Booth <mat.booth@redhat.com> - 1:8.8.1-8
- Use global instead of define
- Move more bundles into SDK that should be there
- Remove forbidden SCL macros
- Minor other changes to make it easier to auto-SCLise

* Mon Feb 29 2016 Alexander Kurtakov <akurtako@redhat.com> 1:8.8.1-7
- Update to upstream 8.8.1 release.

* Mon Feb 29 2016 Mat Booth <mat.booth@redhat.com> - 1:8.8.0-7.2
- Rebuild 2016-02-29

* Tue Feb 16 2016 Mat Booth <mat.booth@redhat.com> - 1:8.8.0-7.1
- Import latest from Fedora

* Tue Feb 09 2016 Roland Grunberg <rgrunber@redhat.com> - 1:8.8.0-7
- Update to use proper xmvn provided macros.
- Fix CDT GDB Standalone Debugger.

* Thu Feb 04 2016 Roland Grunberg <rgrunber@redhat.com> - 1:8.8.0-6
- Add symbolic links for google-gson and apache-commons-compress in arduino.
- Resolves: rhbz#1302131.

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1:8.8.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Nov 23 2015 Alexander Kurtakov <akurtako@redhat.com> 1:8.8.0-4
- Drop old patches and organize them.

* Thu Oct 08 2015 Mat Booth <mat.booth@redhat.com> - 1:8.8.0-3
- Perform full build
- Exclude docker plugins on Fedora < 23

* Thu Oct 8 2015 Alexander Kurtakov <akurtako@redhat.com> 1:8.8.0-2
- Split qt feature into subpackage with proper deps to qml, qtquick, qmake so generated project works.
- Disable brp-repack script as it just slows down the build.

* Wed Oct 07 2015 Mat Booth <mat.booth@redhat.com> - 1:8.8.0-1
- Update to Mars.1 release
- Bootstrap mode for secondary arches

* Mon Sep 21 2015 Jeff Johnston <jjohnstn@redhat.com> - 1:8.7.0-10
- Fix missing test resources
- Fix missing exit code in console

* Tue Aug 04 2015 Roland Grunberg <rgrunber@redhat.com> - 1:8.7.0-9
- Add script for automatically launching CDT Test Bundles.

* Fri Jul 10 2015 Mat Booth <mat.booth@redhat.com> - 1:8.7.0-8
- No longer R/BR nekohtml

* Tue Jul 07 2015 Jeff Johnston <jjohnstn@redhat.com> 1:8.7.0-7
- Change macro controlling docker support to also control remote support
- Disable autotools and remote plug-ins/features if macro is 0
- This allows boot-strapping CDT for use by eclipse-remote and
  eclipse-linuxtools-docker packages
 
* Thu Jul 02 2015 Jeff Johnston <jjohnstn@redhat.com> 1:8.7.0-6
- Add missing src file test resources referred to by test cases.

* Mon Jun 29 2015 Jeff Johnston <jjohnstn@redhat.com> 1:8.7.0-5
- Fix for bug 1235942.
- Fix up some dependencies in the config.ini file that have changed their
  OSGI reference in rawhide.

* Fri Jun 26 2015 Jeff Johnston <jjohnstn@redhat.com> 1:8.7.0-4
- Fix for bug 1235942.
- Add back patch3 which is needed to set up the config.ini file properly.
- Also add some new dependencies to the config.ini file that were added
  as part of CDT 8.7.

* Fri Jun 26 2015 Jeff Johnston <jjohnstn@redhat.com> 1:8.7.0-3
- Fix for bug 1235945.
- Move Docker launcher plug-ins to own package: eclipse-cdt-docker.

* Thu Jun 25 2015 Jeff Johnston <jjohnstn@redhat.com> 1:8.7.0-2
- Use simpler macro to control container support and fix macro tests.

* Tue Jun 23 2015 Jeff Johnston <jjohnstn@redhat.com> 1:8.7.0-1
- Switch to use CDT_8_7 tag.
- Add with conditional to remove container support or add it in.

* Mon Jun 15 2015 Alexander Kurtakov <akurtako@redhat.com> 1:8.7.0-0.6.gitd13a53c
- Fix build with Tycho 0.23.
- Update to newer snapshot.
- Drop rse R as it's autogen.

* Thu Jun 4 2015 Alexander Kurtakov <akurtako@redhat.com> 1:8.7.0-0.5.git6c36f7f
- Disable jacoco plugin and remove useless directory from the build.

* Thu Jun 4 2015 Alexander Kurtakov <akurtako@redhat.com> 1:8.7.0-0.4.git6c36f7f
- Add arduino subpackage and enable building arduino plugins.

* Wed Jun 3 2015 Alexander Kurtakov <akurtako@redhat.com> 1:8.7.0-0.3.git6c36f7f
- Drop Linux Tools libhover compilation and Recommend eclipse-linuxtools-libhover instead. 

* Wed Jun 3 2015 Alexander Kurtakov <akurtako@redhat.com> 1:8.7.0-0.2.git6c36f7f
- Newer snapshot.
- Enable remote feature now that deps are available.
- Drop Group tags.

* Mon Jun 1 2015 Alexander Kurtakov <akurtako@redhat.com> 1:8.7.0-0.1.git136c034
- Update to 8.7.0 pre-release.
