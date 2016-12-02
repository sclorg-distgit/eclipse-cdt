%{?scl:%scl_package eclipse-cdt}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

%global baserelease 9

# Change following to 0 to default to no container/remote support when building for 
# first time in a release...this is needed to build eclipse-linuxtools-docker and
# eclipse.remote which are circular dependencies of eclipse-cdt
%global _enable_container_and_remote_support 1
%global _enable_container_support 1

Epoch: 1

%global major                   9
%global minor                   0
%global majmin                  %{major}.%{minor}
%global micro                   0
%global eclipse_base            %{_libdir}/eclipse
%global cdt_snapshot            org.eclipse.cdt-CDT_9_0_0
%global template_snapshot       org.eclipse.tools.templates-e87ce036ebc1ac86d1aaee807e4d9ff1759b61d9

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

# Desktop file information
%global app_name %{?app_name_prefix} Eclipse C/C++ Debugger
%global app_exec %{?app_exec_prefix} cdtdebug

Summary:        Eclipse C/C++ Development Tools (CDT) plugin
Name:           %{?scl_prefix}eclipse-cdt
Version:        %{majmin}.%{micro}
Release:        2.%{baserelease}%{?dist}
License:        EPL and CPL
URL:            http://www.eclipse.org/cdt

Source0: http://git.eclipse.org/c/cdt/org.eclipse.cdt.git/snapshot/%{cdt_snapshot}.tar.xz

# This could be broken out into a separate SRPM if another project starts using it
Source1: http://git.eclipse.org/c/cdt/org.eclipse.tools.templates.git/snapshot/%{template_snapshot}.tar.xz

Source3: eclipse-cdt.desktop

# man-page for /usr/bin/cdtdebug
Source4: cdtdebug.man

# Script to run the tests in Xvnc
Source5: %{pkg_name}-runtests.sh

# Following fixes cdtdebug.sh script to get proper platform filesystem plugin
Patch1: %{pkg_name}-cdtdebug.patch

# Following fixes Standalone Debugger config.ini file to use bundle symbolic names
Patch2: %{pkg_name}-config-ini.patch

# Following fixes Standalone Debugger README file to refer to /usr/bin/cdtdebug
Patch3: %{pkg_name}-cdtdebug-readme.patch

%if ! %{_enable_container_and_remote_support}
Patch4: bootstrap.patch
%endif

BuildRequires: %{?scl_prefix}tycho
BuildRequires: %{?scl_prefix}tycho-extras
BuildRequires: %{?scl_prefix}eclipse-license
BuildRequires: desktop-file-utils
BuildRequires: %{?scl_prefix}lpg-java-compat
BuildRequires: %{?scl_prefix_java_common}google-gson
BuildRequires: %{?scl_prefix}eclipse-platform
BuildRequires: %{?scl_prefix}eclipse-pde
BuildRequires: %{?scl_prefix}eclipse-contributor-tools
BuildRequires: %{?scl_prefix}eclipse-swtbot >= 2.4.0
BuildRequires: %{?scl_prefix_maven}exec-maven-plugin
BuildRequires: %{?scl_prefix_maven}maven-antrun-plugin
BuildRequires: %{?scl_prefix}freemarker
BuildRequires: %{?scl_prefix}mockito
%if %{_enable_container_and_remote_support}
%if %{_enable_container_support}
BuildRequires: %{?scl_prefix}eclipse-linuxtools-docker
%endif
BuildRequires: %{?scl_prefix}eclipse-remote >= 2.1.0
BuildRequires: %{?scl_prefix}eclipse-launchbar
%endif

Requires:      gdb make gcc-c++
%if %{_enable_container_and_remote_support}
Requires:      autoconf automake libtool
Requires:      %{?scl_prefix}eclipse-remote >= 2.1.0
Requires:      %{?scl_prefix}eclipse-launchbar
%endif


%description
Eclipse features and plugins that are useful for C and C++ development.

%package parsers
Summary:        Eclipse C/C++ Development Tools (CDT) Optional Parsers
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       %{?scl_prefix}lpg-java-compat

%description parsers
Optional language-variant parsers for the CDT.

%package llvm
Summary:        Eclipse C/C++ Development Tools (CDT) LLVM
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       %{?scl_prefix}lpg-java-compat
%if ! 0%{?rhel}
Requires:       clang
%endif

%description llvm
Optional llvm parsers for the CDT.

%if %{_enable_container_and_remote_support}

%if %{_enable_container_support}
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
%if ! 0%{?rhel}
#for qmake
Requires:       qt5-qtbase-devel
#for new qt project to work out of the box
Requires:       pkgconfig(Qt5Qml)
Requires:       pkgconfig(Qt5Quick)
%endif

%description qt
Extensions to support Qt projects and objects in the indexer.

%endif

%package tests
Summary:        Eclipse C/C++ Development Tools (CDT) Tests
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       %{name}-parsers = %{epoch}:%{version}-%{release}
Requires:       %{name}-llvm = %{epoch}:%{version}-%{release}
%if %{_enable_container_and_remote_support}
Requires:       %{name}-docker = %{epoch}:%{version}-%{release}
Requires:       %{name}-qt = %{epoch}:%{version}-%{release}
%endif
Requires:       %{?scl_prefix}eclipse-tests
Requires:       %{?scl_prefix}eclipse-swtbot >= 2.4.0

%description tests
Test plugins for the CDT.

%package sdk
Summary:        Eclipse C/C++ Development Tools (CDT) SDK plugin
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       %{?scl_prefix}eclipse-pde

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

%patch1 -p1 -b orig
%patch2 -p1
%patch3 -p1

# Fix tycho target environment
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
pushd org.eclipse.cdt.core.linux
sed -i -e 's/x86/%{eclipse_arch}/g' pom.xml
popd
popd
pushd releng/org.eclipse.cdt.native-feature
sed -i -e 's/"org.eclipse.cdt.core.linux.x86"/"org.eclipse.cdt.core.linux.%{eclipse_arch}"/g' feature.xml
sed -i -e 's/arch="x86"/arch="%{eclipse_arch}"/' feature.xml
popd
sed -i -e "s|org.eclipse.cdt.core.linux.x86</module>|org.eclipse.cdt.core.linux.%{eclipse_arch}</module>|g" pom.xml
%endif

# Force the arch-specific plug-ins to be dir-shaped so that binary stripping works and the native files
# aren't loaded into the user.home .eclipse configuration
echo "Eclipse-BundleShape: dir" >> core/org.eclipse.cdt.core.linux.%{eclipse_arch}/META-INF/MANIFEST.MF
echo "Eclipse-BundleShape: dir" >> native/org.eclipse.cdt.native.serial/META-INF/MANIFEST.MF
sed -i -e '/library/s/library\//library\/*.c,library\/*.h,library\/Makefile/' \
  core/org.eclipse.cdt.core.linux/build.properties

# Remove pre-built natives
rm -rf native/org.eclipse.cdt.native.serial/os/* \
       core/org.eclipse.cdt.core.linux.*/os/*
mkdir -p native/org.eclipse.cdt.native.serial/os/linux/%{eclipse_arch} \
         core/org.eclipse.cdt.core.linux.%{eclipse_arch}/os/linux/%{eclipse_arch}

# Don't use the target configuration
%pom_disable_module releng/org.eclipse.cdt.target
%pom_xpath_remove "pom:configuration/pom:target"

# Don't need to build the repo
%pom_disable_module releng/org.eclipse.cdt.repo
%pom_disable_module releng/org.eclipse.cdt.testing.repo

# Disable the jgit provider and force default packaging
%pom_remove_plugin org.eclipse.tycho:tycho-packaging-plugin
%pom_remove_plugin org.jacoco:jacoco-maven-plugin

# Disable docker, autotools, and remote features if we are building a boot-strap build
%if ! %{_enable_container_and_remote_support}
%patch4
%pom_disable_module launch/org.eclipse.cdt.docker.launcher
%pom_disable_module launch/org.eclipse.cdt.docker.launcher-feature
%pom_disable_module launch/org.eclipse.cdt.docker.launcher.source-feature
%pom_disable_module build/org.eclipse.cdt.autotools.core
%pom_disable_module build/org.eclipse.cdt.autotools.docs
%pom_disable_module build/org.eclipse.cdt.autotools.tests
%pom_disable_module build/org.eclipse.cdt.autotools.ui
%pom_disable_module build/org.eclipse.cdt.autotools.ui.tests
%pom_disable_module build/org.eclipse.cdt.autotools-feature
%pom_disable_module build/org.eclipse.cdt.autotools.source-feature
%pom_disable_module cross/org.eclipse.cdt.launch.remote
%pom_disable_module cross/org.eclipse.cdt.launch.remote-feature
%pom_disable_module qt/org.eclipse.cdt.qt.core
%pom_disable_module qt/org.eclipse.cdt.qt.ui
%pom_disable_module qt/org.eclipse.cdt.qt.ui.tests
%pom_disable_module qt/org.eclipse.cdt.qt-feature
%pom_disable_module build/org.eclipse.cdt.cmake.core
%pom_disable_module build/org.eclipse.cdt.cmake.ui
%pom_disable_module build/org.eclipse.cdt.cmake-feature
%pom_disable_module remote/org.eclipse.cdt.remote.core
%pom_disable_module remote/org.eclipse.cdt.remote-feature
%else
%if ! %{_enable_container_support}
%pom_disable_module launch/org.eclipse.cdt.docker.launcher
%pom_disable_module launch/org.eclipse.cdt.docker.launcher-feature
%pom_disable_module launch/org.eclipse.cdt.docker.launcher.source-feature
%endif
%endif
%pom_disable_module toolchains/arduino/org.eclipse.cdt.arduino.core
%pom_disable_module toolchains/arduino/org.eclipse.cdt.arduino.ui
%pom_disable_module toolchains/arduino/org.eclipse.cdt.arduino-feature

for b in `ls core/ | grep -P -e 'org.eclipse.cdt.core\.(?!linux\.%{eclipse_arch}$|tests$|linux$|native$)'` ; do
  module=$(grep ">core/$b<" pom.xml || :)
  if [ -n "$module" ] ; then
    %pom_disable_module core/$b
    %pom_xpath_remove "plugin[@id='$b']" releng/org.eclipse.cdt.native-feature/feature.xml
  fi
done
for b in aix macosx win32 ; do
  %pom_xpath_remove "plugin[@id='org.eclipse.cdt.core.$b.source']" releng/org.eclipse.cdt.native.source-feature/feature.xml
done

# Fix hamcrest and mockito deps
sed -i -e 's/org.mockito/org.mockito.mockito-core/' -e 's/org.hamcrest/org.hamcrest.core/' \
  dsf-gdb/org.eclipse.cdt.tests.dsf.gdb/META-INF/MANIFEST.MF
%pom_disable_module dsf-gdb/org.eclipse.cdt.tests.dsf.gdb
%pom_xpath_remove "plugin[@id='org.eclipse.cdt.tests.dsf.gdb']" releng/org.eclipse.cdt.testing-feature/feature.xml

# Add template tools to the build
tar xf %{SOURCE1} --strip-components=1 --exclude=%{template_snapshot}/pom.xml
for b in org.eclipse.tools.templates.{core,freemarker,ui} ; do
  %pom_xpath_inject "pom:modules" "<module>bundles/$b</module>"
  %pom_set_parent "org.eclipse.cdt:cdt-parent:%{version}-SNAPSHOT" bundles/$b
  %pom_xpath_inject "pom:parent" "<relativePath>../../pom.xml</relativePath>" bundles/$b
done

# Fix freemarker dep
sed -i -e 's/org.freemarker/org.freemarker.freemarker/' \
  qt/org.eclipse.cdt.qt.core/META-INF/MANIFEST.MF \
  bundles/org.eclipse.tools.templates.freemarker/META-INF/MANIFEST.MF \
  build/org.eclipse.cdt.cmake.core/META-INF/MANIFEST.MF

# Drop unnecessary dep on log4j
sed -i -e '/log4j/d' build/org.eclipse.cdt.autotools.ui.tests/META-INF/MANIFEST.MF

# Remove org.eclipse.cdt.launch.remote.source to prevent cycle back to SDK
%pom_xpath_remove "plugin[@id='org.eclipse.cdt.launch.remote.source']" cross/org.eclipse.cdt.launch.remote-feature/feature.xml

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
%mvn_package :org.eclipse.tools.templates.*
%mvn_package :org.eclipse.cdt.arduino* arduino
%mvn_package :org.eclipse.cdt.docker* docker
%mvn_package :org.eclipse.cdt.managedbuilder.llvm* llvm
%mvn_package :org.eclipse.cdt.qt* qt
%mvn_package :org.eclipse.cdt.cmake* qt
%mvn_package :org.eclipse.cdt*
%{?scl:EOF}


%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
export JAVA_HOME=%{_jvmdir}/java

# Build native serial library
pushd native/org.eclipse.cdt.native.serial/jni
make ../os/linux/%{eclipse_arch}/libserial.so
popd

# Exclude EquinoxResolver to avoid NPE occuring on arm
%ifarch %{arm}
export MAVEN_OPTS="-XX:CompileCommand=exclude,org/eclipse/tycho/core/osgitools/EquinoxResolver,newState"
%endif

%mvn_build -j -f -- -Dtycho.local.keepTarget -Dskip-ppc64le -Dnative=linux.%{eclipse_arch}
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

pushd %{buildroot}%{eclipse_base}/droplets/cdt/eclipse/plugins
DEBUGAPPLICATIONVERSION=$(ls . | grep org.eclipse.cdt.debug.application_ | sed 's/org.eclipse.cdt.debug.application_//' |sed 's/.jar//')
pushd org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION
# Create the jar file inside the folder to work around issue where standalone application cannot be found without a jar file
jar -cfmv org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION.jar META-INF/MANIFEST.MF *
popd

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
  sed -i -e "s,${PLUGIN%_*}\,,file\\\\:%{eclipse_base}/droplets/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
done

sed -i -e "s,org.eclipse.cdt.debug.application\,,file\\\\:%{eclipse_base}/droplets/cdt/eclipse/plugins/org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION.jar\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini

sed -i -e "s,cp config.ini,cp %{eclipse_base}/droplets/cdt/eclipse/plugins/org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/cdtdebug.sh
sed -i -e "s,cp dev.properties,cp %{eclipse_base}/droplets/cdt/eclipse/plugins/org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/dev.properties," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/cdtdebug.sh
install -D -m 755 org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/cdtdebug.sh $binInstallDir/cdtdebug
popd

echo %{eclipse_base}/droplets/cdt/eclipse/plugins/org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION.jar >> .mfiles

# Install icons
install -D debug/org.eclipse.cdt.debug.application/icons/cc32.png \
    $RPM_BUILD_ROOT/usr/share/icons/hicolor/32x32/apps/%{name}.png
install -D debug/org.eclipse.cdt.debug.application/icons/cc48.png \
    $RPM_BUILD_ROOT/usr/share/icons/hicolor/48x48/apps/%{name}.png
install -D debug/org.eclipse.cdt.debug.application/icons/cc128.png \
    $RPM_BUILD_ROOT/usr/share/icons/hicolor/128x128/apps/%{name}.png
install -D debug/org.eclipse.cdt.debug.application/icons/cc.png \
    $RPM_BUILD_ROOT/usr/share/icons/hicolor/256x256/apps/%{name}.png
install -d $RPM_BUILD_ROOT/usr/share/pixmaps
ln -s /usr/share/icons/hicolor/256x256/apps/%{name}.png \
    $RPM_BUILD_ROOT/usr/share/pixmaps/%{name}.png

# Fix permissions on native libraries
find $RPM_BUILD_ROOT -name *.so -exec chmod +x {} \;

# Install desktop file
sed -i -e 's|Exec=cdtdebug|Exec=%{app_exec}|g' desktop/eclipse-cdt.desktop
sed -i -e 's|Name=Eclipse.*|Name=%{app_name}|g' desktop/eclipse-cdt.desktop
sed -i -e "s|Icon=eclipse|Icon=%{name}|g" desktop/eclipse-cdt.desktop
install -D desktop/eclipse-cdt.desktop $RPM_BUILD_ROOT/usr/share/applications/%{name}.desktop
desktop-file-validate $RPM_BUILD_ROOT/usr/share/applications/%{name}.desktop

# man page
cp man/cdtdebug.man $manInstallDir/cdtdebug.1
%{?scl:EOF}


%files -f .mfiles
%{_bindir}/cdtdebug
/usr/share/applications/*
/usr/share/pixmaps/*
/usr/share/icons/*/*/apps/*
%{_mandir}/man1/cdtdebug.1*
%doc releng/org.eclipse.cdt.sdk/epl-v10.html
%doc releng/org.eclipse.cdt.sdk/notice.html

%files sdk -f .mfiles-sdk
%doc releng/org.eclipse.cdt.sdk/epl-v10.html
%doc releng/org.eclipse.cdt.sdk/notice.html

%files parsers -f .mfiles-parsers
%doc releng/org.eclipse.cdt.sdk/epl-v10.html
%doc releng/org.eclipse.cdt.sdk/notice.html

%files tests -f .mfiles-tests
%{_bindir}/eclipse-runCDTTestBundles
%doc releng/org.eclipse.cdt.sdk/epl-v10.html
%doc releng/org.eclipse.cdt.sdk/notice.html

%files llvm -f .mfiles-llvm
%doc releng/org.eclipse.cdt.sdk/epl-v10.html
%doc releng/org.eclipse.cdt.sdk/notice.html

%if %{_enable_container_and_remote_support}

%files qt -f .mfiles-qt
%doc releng/org.eclipse.cdt.sdk/epl-v10.html
%doc releng/org.eclipse.cdt.sdk/notice.html

%if %{_enable_container_support}
%files docker -f .mfiles-docker
%doc releng/org.eclipse.cdt.sdk/epl-v10.html
%doc releng/org.eclipse.cdt.sdk/notice.html
%endif
%endif

%changelog
* Mon Sep 12 2016 Roland Grunberg <rgrunber@redhat.com> - 1:9.0.0-2.9
- Break cycle from main CDT package to the SDK.
- Resolves: rhbz#1373096.

* Tue Aug 02 2016 Mat Booth <mat.booth@redhat.com> - 1:9.0.0-2.8
- Fix permissions on native libraries

* Tue Aug 02 2016 Mat Booth <mat.booth@redhat.com> - 1:9.0.0-2.7
- Fix binary stripping

* Tue Aug 02 2016 Mat Booth <mat.booth@redhat.com> - 1:9.0.0-2.6
- Fix launching stand-alone debugger

* Fri Jul 29 2016 Mat Booth <mat.booth@redhat.com> - 1:9.0.0-2.5
- Fix tests are uninstallable

* Fri Jul 29 2016 Mat Booth <mat.booth@redhat.com> - 1:9.0.0-2.4
- Perform full non-bootstrap build

* Fri Jul 29 2016 Mat Booth <mat.booth@redhat.com> - 1:9.0.0-2.3
- Enable remote bits

* Fri Jul 29 2016 Mat Booth <mat.booth@redhat.com> - 1:9.0.0-2.2
- Perform a bootstrap build
- Fix non-bootstrap requires

* Fri Jul 29 2016 Mat Booth <mat.booth@redhat.com> - 1:9.0.0-2.1
- Auto SCL-ise package for rh-eclipse46 collection

* Fri Jul 29 2016 Mat Booth <mat.booth@redhat.com> - 1:9.0.0-2
- Fix bootstrapping mode

* Wed Jun 22 2016 Mat Booth <mat.booth@redhat.com> - 1:9.0.0-1
- Update to Neon release

* Wed Jun 15 2016 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:9.0.0-0.9.gitdff6b3b
- Add missing build-requires

* Mon Jun 06 2016 Jeff Johnston <jjohnstn@redhat.com> - 1:9.0.0-0.9.gitdff6b3b
- Move location code to find launchbar.core and ui.views.log into cdtdebug script
- Move setting of jar files for gson, xerces, xalan, xml.resolver, xml.serializer,
  and lucene.analysis into config.ini patch

* Thu Jun 02 2016 Jeff Johnston <jjohnstn@redhat.com> - 1:9.0.0-0.8.gitdff6b3b
- Update section of spec file that modifies standalone debugger config.ini
- Find org.eclipse.launchbar.core and org.eclipse.ui.views.log plugins
- Set jar files for com.google.gson, org.apache.xerces, org.apache.xalan,
  org.apache.xml.resolver, org.apache.xml.serializer, org.apache.lucene.analysis

* Mon May 30 2016 Jeff Johnston <jjohnstn@redhat.com> - 1:9.0.0-0.7.gitdff6b3b
- Add Requires eclipse-launchbar which is now required by standalone debugger

* Sat May 21 2016 Mat Booth <mat.booth@redhat.com> - 1:9.0.0-0.6.gitdff6b3b
- Add a patch to fix LLVM documentation, ebz#459567
- Drop unneeded BR on RSE

* Thu May 12 2016 Alexander Kurtakov <akurtako@redhat.com> 1:9.0.0-0.5.gitdff6b3b
- Fix natives compile for profiles not included upstream.

* Thu May 12 2016 Alexander Kurtakov <akurtako@redhat.com> 1:9.0.0-0.4.gitdff6b3b
- New snapshot with natives build hooked in the maven build.

* Tue May 03 2016 Mat Booth <mat.booth@redhat.com> - 1:9.0.0-0.3.git0b93e81
- Fix launching stand-alone debugger

* Mon May 02 2016 Sopot Cela <scela@redhat.com> - 1:9.0.0-0.2.git0b93e81
- Fix broken reference to license issue to fix the build

* Sun May 01 2016 Mat Booth <mat.booth@redhat.com> - 1:9.0.0-0.1.git0b93e81
- Update to latest snapshot for Neon support

* Thu Mar 10 2016 Mat Booth <mat.booth@redhat.com> - 1:8.8.1-9
- Make standalone debugger work with all versions of lucene

* Thu Mar 10 2016 Mat Booth <mat.booth@redhat.com> - 1:8.8.1-8
- Use global instead of define
- Move more bundles into SDK that should be there
- Remove forbidden SCL macros
- Minor other changes to make it easier to auto-SCLise

* Mon Feb 29 2016 Alexander Kurtakov <akurtako@redhat.com> 1:8.8.1-7
- Update to upstream 8.8.1 release.

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
