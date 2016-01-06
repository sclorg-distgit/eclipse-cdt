%{?scl:%scl_package eclipse-cdt}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}


%global debug_package %{nil}
%global _enable_debug_packages 0

# Change following to 0 to default to no container/remote support when building for 
# first time in a release...this is needed to build eclipse-linuxtools-docker and
# eclipse.remote which are circular dependencies of eclipse-cdt.  Disable both
# first to build eclipse-remote.  Later, enable linuxtools when linuxtools is built.
%global _enable_remote 1
%global _enable_linuxtools 1

Epoch: 1

%define major                   8
%define minor                   7
%define majmin                  %{major}.%{minor}
%define micro                   0
%define eclipse_base            %{_libdir}/eclipse
%define cdt_snapshot		org.eclipse.cdt-CDT_8_7_0

# All arches line up except i386 -> x86
%ifarch %{ix86}
%define eclipse_arch    x86
%else
%ifarch %{arm}
%define eclipse_arch    arm
%else
%define eclipse_arch    %{_arch}
%endif
%endif

Summary:        Eclipse C/C++ Development Tools (CDT) plugin
Name:           %{?scl_prefix}eclipse-cdt
Version:        %{majmin}.%{micro}
Release:        8.bs2%{?dist}
License:        EPL and CPL
URL:            http://www.eclipse.org/cdt

Source0: http://git.eclipse.org/c/cdt/org.eclipse.cdt.git/snapshot/%{cdt_snapshot}.tar.xz

Source3: eclipse-cdt.desktop

# man-page for /usr/bin/cdtdebug
Source4: cdtdebug.man

# Script to run the tests in Xvnc
Source5: %{pkg_name}-runtests.sh

Patch0: %{pkg_name}-tycho-build.patch

# Following adds current directory to autotools tests build.properties
Patch1: %{pkg_name}-autotools-test.patch

# Following fixes cdtdebug.sh script to get proper platform filesystem plugin
Patch2: %{pkg_name}-cdtdebug.patch

# Following fixes Standalone Debugger config.ini file to use bundle symbolic names
Patch3: %{pkg_name}-config-ini.patch

# Following fixes Standalone Debugger README file to refer to /usr/bin/cdtdebug
Patch4: %{pkg_name}-cdtdebug-readme.patch

# Following fixes jetty reqs in CDT target
Patch5: %{pkg_name}-target.patch

# Following removes docker launcher plugins from repo
Patch6: remove-docker.patch

# Following removes autotools and remote plugins from repo
Patch7: remove-remote.patch

# Following removes arduino plug-ins/feature
Patch8: remove-arduino.patch

# Following adds missing java resources to tests
Patch9: %{pkg_name}-test-resources.patch

# Following fixes Bug 1261915 - missing exit code in console
Patch10: %{pkg_name}-exit-code.patch

# Following also needed to fix Bug 1261915 - missing exit code in console
Patch11: %{pkg_name}-gdbversion.patch

BuildRequires: %{?scl_prefix}tycho
BuildRequires: %{?scl_prefix}tycho-extras
BuildRequires: %{?scl_prefix}eclipse-pde >= 1:4.3.0
BuildRequires: %{?scl_prefix}eclipse-license
BuildRequires: %{?scl_prefix_java_common}maven-local
BuildRequires: desktop-file-utils
BuildRequires: %{?scl_prefix}lpg-java-compat
BuildRequires: %{?scl_prefix}eclipse-platform >= 1:4.3.0
BuildRequires: %{?scl_prefix}eclipse-tests >= 1:4.3.0
BuildRequires: %{?scl_prefix}eclipse-swtbot
BuildRequires: %{?scl_prefix_maven}exec-maven-plugin
%if %{_enable_linuxtools}
BuildRequires: %{?scl_prefix}eclipse-linuxtools-docker
%endif
%if %{_enable_remote}
BuildRequires: %{?scl_prefix}eclipse-remote
BuildRequires: %{?scl_prefix}eclipse-rse
%endif

Requires:      %{?scl_prefix}gdb make %{?scl_prefix}gcc-c++
%if %{_enable_remote}
Requires:      autoconf automake libtool
Requires:      %{?scl_prefix}eclipse-remote
%endif
%if %{_enable_linuxtools}
Requires:      %{?scl_prefix}eclipse-linuxtools-libhover
%endif

%description
Eclipse features and plugins that are useful for C and C++ development.

%package parsers
Summary:        Eclipse C/C++ Development Tools (CDT) Optional Parsers
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       %{?scl_prefix}lpg-java-compat

%description parsers
Optional language-variant parsers for the CDT.

%if %{_enable_linuxtools} == 1

%package docker
Summary:	C/C++ Docker Launcher
Requires:      %{name} = %{epoch}:%{version}-%{release}
Requires:	%{?scl_prefix}eclipse-linuxtools-docker

%description docker
Special launcher for CDT to allow launching and debugging C/C++ applications
in Docker Containers.

%endif

%package tests
Summary:	Eclipse C/C++ Development Tools (CDT) Tests
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
%patch4 -p1
%patch5 -p1
%patch8 -p0
%patch9 -p0
%patch10 -p1
%patch11 -p1
%if %{_enable_linuxtools} == 0
%patch6 -p0
%endif
%if %{_enable_remote} == 0
%patch7 -p0
%endif

sed -i -e 's/<arch>x86<\/arch>/<arch>%{eclipse_arch}<\/arch>/g' pom.xml
# Add secondary arch support if we are building there
%ifarch %{arm} s390 s390x aarch64
pushd core
pushd org.eclipse.cdt.core.native
sed -i -e 's/linux.x86 /linux.%{eclipse_arch} /g' plugin.properties
sed -i -e 's/\\(x86\\)/(%{eclipse_arch})/g' plugin.properties
popd
cp -r org.eclipse.cdt.core.linux.x86 org.eclipse.cdt.core.linux.%{eclipse_arch}
rm -fr org.eclipse.cdt.core.linux.x86
pushd org.eclipse.cdt.core.linux
sed -i -e 's/<arch>x86<\/arch>/<arch>%{eclipse_arch}<\/arch>/g' pom.xml
popd
pushd org.eclipse.cdt.core.linux.%{eclipse_arch}
sed -i -e 's/x86/%{eclipse_arch}/g' pom.xml
pushd META-INF
sed -i -e 's/x86/%{eclipse_arch}/g' MANIFEST.MF
popd
pushd os/linux
mv x86 %{eclipse_arch}
popd
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

# Disable the jgit provider and force default packaging
%pom_remove_plugin org.eclipse.tycho:tycho-packaging-plugin
%pom_remove_plugin org.jacoco:jacoco-maven-plugin

# Disable docker, autotools, and remote features if we are building a boot-strap build
%if %{_enable_linuxtools} == 0
%pom_disable_module launch/org.eclipse.cdt.docker.launcher
%pom_disable_module launch/org.eclipse.cdt.docker.launcher-feature
%pom_disable_module launch/org.eclipse.cdt.docker.launcher.source-feature
%endif
%if %{_enable_remote} == 0
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
%endif

# Remove arduino
%pom_disable_module toolchains/arduino/org.eclipse.cdt.arduino.core
%pom_disable_module toolchains/arduino/org.eclipse.cdt.arduino.ui
%pom_disable_module toolchains/arduino/org.eclipse.cdt.arduino-feature

# Remove p2 installer
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

sed -i -e "s|org.junit|org.hamcrest.core, org.junit|g" dsf-gdb/org.eclipse.cdt.tests.dsf.gdb/META-INF/MANIFEST.MF

%{?scl:EOF}

%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}

export JAVA_HOME=%{java_home}

# Exclude EquinoxResolver to avoid NPE occuring on arm
%ifarch %{arm}
export MAVEN_OPTS="-XX:CompileCommand=exclude,org/eclipse/tycho/core/osgitools/EquinoxResolver,newState"
%endif

pushd core/org.eclipse.cdt.core.linux/library
make JAVA_HOME="/usr/lib/jvm/java" ARCH=%{eclipse_arch} CC='gcc -D_GNU_SOURCE'
popd

xmvn -o -Dtycho.local.keepTarget -Dskip-ppc64le -Dmaven.test.skip=true -Dmaven.repo.local=`pwd`/.m2 install

%{?scl:EOF}

%install

installDir=${RPM_BUILD_ROOT}/%{eclipse_base}/dropins/cdt
testInstallDir=${RPM_BUILD_ROOT}/%{_javadir}/eclipse-cdt-tests/plugins
parsersInstallDir=${installDir}-parsers
%if %{_enable_linuxtools} == 1
dockerInstallDir=${installDir}-docker
%endif
sdkInstallDir=${installDir}-sdk
binInstallDir=${RPM_BUILD_ROOT}/%{_bindir}
manInstallDir=${RPM_BUILD_ROOT}/%{_mandir}/man1
install -d -m755 $installDir
install -d -m755 $parsersInstallDir
install -d -m755 $sdkInstallDir
install -d -m755 $testInstallDir
install -d -m755 $binInstallDir
install -d -m755 $manInstallDir
%if %{_enable_linuxtools} == 1
install -d -m755 $dockerInstallDir
%endif

# Unzip contents of the cdt repo, removing all but plugins and features
unzip -q -o releng/org.eclipse.cdt.repo/target/org.eclipse.cdt.repo.zip \
-d $installDir/eclipse

#tests
# We need grep to return non-zero status to skip all non eclipse-test-plugins
set +e
for pom in `find . -name pom.xml`; do
 grep -q '<packaging>eclipse-test-plugin</packaging>' ${pom}
 if [ $? -eq 0 ]; then
   testjar=`ls ${pom/pom.xml/}'target/'*.jar | grep -v sources`
   cp ${testjar} ${testInstallDir}
 fi
done
set -e

# Unzip CDT Standalone Debug plugin which contains installation scripts for the end-user to use
pushd ${installDir}/eclipse/plugins
DEBUGAPPLICATIONVERSION=$(ls . | grep org.eclipse.cdt.debug.application_ | sed 's/org.eclipse.cdt.debug.application_//' |sed 's/.jar//')
unzip org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION.jar -d ./org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION
# Copy the jar file inside the folder to work around issue where standalone application cannot be found without a jar file
mv org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION.jar org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/org.eclipse.cdt.debug.application.jar
# Fix the cdtdebug.sh script to hard-code ECLIPSE_HOME and cdt dropins directory
sed -i -e "s,@ECLIPSE_HOME@,%{eclipse_base}," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/cdtdebug.sh
sed -i -e "s,@CDT_DROPINS@,%{eclipse_base}/dropins/cdt/eclipse/plugins," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/cdtdebug.sh
# Fix the dropin bundles to have full paths to their respective jar files as Eclipse start-up won't find them otherwise
PLUGIN=$(ls . | grep org.eclipse.cdt.core.linux_)
sed -i -e "s,org.eclipse.cdt.core.linux\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.core_)
sed -i -e "s,org.eclipse.cdt.core\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.debug.ui.memory.floatingpoint_)
sed -i -e "s,org.eclipse.cdt.debug.ui.memory.floatingpoint\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.make.core_)
sed -i -e "s,org.eclipse.cdt.make.core\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.dsf.ui_)
sed -i -e "s,org.eclipse.cdt.dsf.ui\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.debug.ui.memory.traditional_)
sed -i -e "s,org.eclipse.cdt.debug.ui.memory.traditional\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.ui_)
sed -i -e "s,org.eclipse.cdt.ui\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.core_)
sed -i -e "s,org.eclipse.cdt.core\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.debug.application_)
sed -i -e "s,org.eclipse.cdt.debug.application\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN/org.eclipse.cdt.debug.application.jar\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.debug.application.doc_)
sed -i -e "s,org.eclipse.cdt.debug.application.doc\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.dsf.gdb.ui_)
sed -i -e "s,org.eclipse.cdt.dsf.gdb.ui\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.debug.mi.ui_)
sed -i -e "s,org.eclipse.cdt.debug.mi.ui\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.launch_)
sed -i -e "s,org.eclipse.cdt.launch\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.managedbuilder.core_)
sed -i -e "s,org.eclipse.cdt.managedbuilder.core\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.managedbuilder.gnu.ui_)
sed -i -e "s,org.eclipse.cdt.managedbuilder.gnu.ui\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.gdb_)
sed -i -e "s,org.eclipse.cdt.gdb\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.dsf.gdb_)
sed -i -e "s,org.eclipse.cdt.dsf.gdb\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.dsf_)
sed -i -e "s,org.eclipse.cdt.dsf\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.debug.mi.core_)
sed -i -e "s,org.eclipse.cdt.debug.mi.core\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.gdb.ui_)
sed -i -e "s,org.eclipse.cdt.gdb.ui\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.debug.ui.memory.transport_)
sed -i -e "s,org.eclipse.cdt.debug.ui.memory.transport\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.debug.ui.memory.search_)
sed -i -e "s,org.eclipse.cdt.debug.ui.memory.search\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.debug.ui.memory.memorybrowser_)
sed -i -e "s,org.eclipse.cdt.debug.ui.memory.memorybrowser\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.debug.ui_)
sed -i -e "s,org.eclipse.cdt.debug.ui\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.debug.core_)
sed -i -e "s,org.eclipse.cdt.debug.core\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep org.eclipse.cdt.core.native_)
sed -i -e "s,org.eclipse.cdt.core.native\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
PLUGIN=$(ls . | grep 'org.eclipse.cdt.core.linux\..*.jar' | grep -v source)
sed -i -e "s,\$linux.plugin\$\,,file\\\\:%{eclipse_base}/dropins/cdt/eclipse/plugins/$PLUGIN\,," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini
sed -i -e "s,cp config.ini,cp %{eclipse_base}/dropins/cdt/eclipse/plugins/org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/config.ini," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/cdtdebug.sh
sed -i -e "s,cp dev.properties,cp %{eclipse_base}/dropins/cdt/eclipse/plugins/org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/dev.properties," org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/cdtdebug.sh
cp org.eclipse.cdt.debug.application_$DEBUGAPPLICATIONVERSION/scripts/cdtdebug.sh $binInstallDir/cdtdebug
popd

%{?scl: sed -i -e 's/Exec=cdtdebug/Exec=scl enable %{scl_name} cdtdebug/g' desktop/eclipse-cdt.desktop}
%{?scl: sed -i -e 's/Icon=eclipse/Icon=%{?scl_prefix}eclipse/g' desktop/eclipse-cdt.desktop}
%{?scl: sed -i -e 's,Name=Eclipse C/C++ Debugger,Name=DTS Eclipse C/C++ Debugger,g' desktop/eclipse-cdt.desktop}
install -D desktop/eclipse-cdt.desktop $RPM_BUILD_ROOT/%{_root_datadir}/applications/%{?scl_prefix}eclipse-cdt.desktop
desktop-file-validate $RPM_BUILD_ROOT/%{_root_datadir}/applications/%{?scl_prefix}eclipse-cdt.desktop

# man page
cp man/cdtdebug.man $manInstallDir/cdtdebug.1

# Unpack all existing feature jars
for x in $installDir/eclipse/features/*.jar; do
  dirname=`echo $x | sed -e 's:\\(.*\\)\\.jar:\\1:g'`
  mkdir -p $dirname
  unzip -q $x -d $dirname
  rm $x
done 

# Remove lpgjavaruntime jar file
rm -rf $installDir/eclipse/plugins/net.sourceforge.*

# Remove llvm-support features/plugins
rm -rf $installDir/eclipse/plugins/*llvm*
rm -rf $installDir/eclipse/features/*llvm*
rm -rf $testInstallDir/*llvm*

# Move upc, xlc, and lrparser plugins/features to parsers install area.
mkdir -p $parsersInstallDir/eclipse/features $parsersInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*xlc* $parsersInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*xlc* $parsersInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*lrparser* $parsersInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*lrparser* $parsersInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*upc* $parsersInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*upc* $parsersInstallDir/eclipse/plugins
pushd $parsersInstallDir/eclipse/plugins
ln -s %{_javadir}/lpgjavaruntime.jar net.sourceforge.lpg.lpgjavaruntime_1.1.0.jar
popd

%if %{_enable_linuxtools} == 1
# Move docker launcher plugins/features to docker install area.
mkdir -p $dockerInstallDir/eclipse/features $dockerInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*docker* $dockerInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*docker* $dockerInstallDir/eclipse/plugins
%endif

mkdir -p $sdkInstallDir/eclipse/features $sdkInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*source* $sdkInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*source* $sdkInstallDir/eclipse/plugins
mv $installDir/eclipse/plugins/org.eclipse.cdt.doc.isv_* $sdkInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*sdk* $sdkInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*sdk* $sdkInstallDir/eclipse/plugins

rm -rf $installDir/eclipse/features/org.eclipse.cdt.master_*
rm -rf $installDir/eclipse/plugins/org.eclipse.ant.optional.junit_*
rm -rf $installDir/eclipse/plugins/org.eclipse.test_*

# remove repo stuff that shouldn't be in dropins folder
rm -rf $installDir/eclipse/artifacts.jar
rm -rf $installDir/eclipse/content.jar
rm -rf $installDir/eclipse/binary

%files
%{eclipse_base}/dropins/cdt
%{_bindir}/cdtdebug
%{_root_datadir}/applications/*
%{_mandir}/man1/cdtdebug.1*
%doc releng/org.eclipse.cdt.releng/epl-v10.html
%doc releng/org.eclipse.cdt.releng/notice.html

%files sdk
%{eclipse_base}/dropins/cdt-sdk
%doc releng/org.eclipse.cdt.releng/epl-v10.html
%doc releng/org.eclipse.cdt.releng/notice.html

%files parsers
%{eclipse_base}/dropins/cdt-parsers
%doc releng/org.eclipse.cdt.releng/epl-v10.html
%doc releng/org.eclipse.cdt.releng/notice.html

%files tests
%{_javadir}/eclipse-cdt-tests
%doc releng/org.eclipse.cdt.releng/epl-v10.html
%doc releng/org.eclipse.cdt.releng/notice.html

%if %{_enable_linuxtools} == 1
%files docker
%{eclipse_base}/dropins/cdt-docker
%doc releng/org.eclipse.cdt.releng/epl-v10.html
%doc releng/org.eclipse.cdt.releng/notice.html
%endif

%changelog
* Fri Oct 30 2015 Jeff Johnston <jjohnstn@redhat.com> - 1:8.7.0-8
- Fix additional regression in exit not being shown in console on debug
- Resolves: #rhbz1261915

* Thu Sep 17 2015 Jeff Johnston <jjohnstn@redhat.com> - 1:8.7.0-7
- Fix regression in exit code being shown in console on run
- Resolves: #rhbz1261915

* Wed Aug 05 2015 Jeff Johnston <jjohnstn@redhat.com> - 1:8.7.0-6
- Change stand-alone debugger config.ini to use javax.annotation-api
  and go back to using org.eclipse.lucene.analysis
- Resolves: #rhbz1247471

* Thu Jul 30 2015 Jeff Johnston <jjohnstn@redhat.com> - 1:8.7.0-5
- Add missing test resources
- Resolves: #rhbz1236035

* Tue Jul 28 2015 Jeff Johnston <jjohnstn@redhat.com> - 1:8.7.0-4
- Fix stand-alone debugger config.ini to include javax.el-api

* Mon Jul 20 2015 Mat Booth <mat.booth@redhat.com> - 1:8.7.0-3.1
- Apply patches cleanly to avoid shipping leftovers

* Thu Jul 16 2015 Jeff Johnston <jjohnstn@redhat.com> 1:8.7.0-3
- Enable linuxtools so full CDT build occurs.

* Wed Jul 15 2015 Jeff Johnston <jjohnstn@redhat.com> 1:8.7.0-2
- Break up bootstrap into two phases
- Enable remote phase so eclipse-linuxtools can build
- Remove neko and xerces stuff which isn't needed here any more

* Thu Jul 09 2015 Jeff Johnston <jjohnstn@redhat.com> 1:8.7.0-1
- Initial CDT 8.7.0 offering (Mars SR0 release)
- Use macro to control docker and remote support to allow
  boot-strapping CDT for use by eclipse-remote and
  eclipse-linuxtools-docker packages
- Disable autotools and remote plug-ins/features if macro is 0
- Make initial build a non-full-build with macro set to 0
 
