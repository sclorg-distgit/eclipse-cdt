%{?scl:%scl_package eclipse-cdt}
%{!?scl:%global pkg_name %{name}}

%global debug_package %{nil}
%global _enable_debug_packages 0

%{?java_common_find_provides_and_requires}

Epoch: 1

%define major                   8
%define minor                   6
%define majmin                  %{major}.%{minor}
%define micro                   0
%define eclipse_base            %{_libdir}/eclipse
%define cdt_snapshot		CDT_8_6_0
%define linuxtools_snapshot	org.eclipse.linuxtools-3.2.0

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
Release:        1.bootstrap1%{?dist}
License:        EPL and CPL
Group:          Development/Tools
URL:            http://www.eclipse.org/cdt
Requires:       %{?scl_prefix}eclipse-platform

Source0: http://git.eclipse.org/c/cdt/org.eclipse.cdt.git/snapshot/%{cdt_snapshot}.tar.bz2

# For libhover
Source1: http://git.eclipse.org/c/linuxtools/org.eclipse.linuxtools.git/snapshot/%{linuxtools_snapshot}.tar.bz2

Source3: eclipse-cdt.desktop

# man-page for /usr/bin/cdtdebug
Source4: cdtdebug.man

# Script to run the tests in Xvnc
Source5: %{pkg_name}-runtests.sh

# Libhover docs to place locally
Source7: libstdc++-v3.libhover

Patch0: %{pkg_name}-tycho-build.patch

# Following are patches to build libhover libstdcxx plug-in and to supply
# binary libhover data directly in the plug-in itself.
Patch1: %{pkg_name}-libhover-local-libstdcxx.patch
Patch2: %{pkg_name}-libhover-libstdcxx.patch

# Following removes unneeded features from Linux Tools build
Patch3: %{pkg_name}-linuxtools-features.patch

# Following adds current directory to autotools tests build.properties
Patch4: %{pkg_name}-autotools-test.patch

# Following fixes up CDT top-level pom
Patch5: %{pkg_name}-disable-jacoco.patch

# Following fixes problem with junit OSGI bundle version
Patch6: %{pkg_name}-linuxtools-libhover-tests.patch

# Following fixes cdtdebug.sh script to get proper platform filesystem plugin
Patch7: %{pkg_name}-cdtdebug.patch

# Following fixes Standalone Debugger config.ini file to use bundle symbolic names
Patch8: %{pkg_name}-config-ini.patch

# Following fixes Standalone Debugger README file to refer to /usr/bin/cdtdebug
Patch9: %{pkg_name}-cdtdebug-readme.patch

# Following fixes jetty reqs in CDT target
Patch10: %{pkg_name}-target.patch

BuildRequires: %{?scl_prefix}tycho
BuildRequires: %{?scl_prefix}tycho-extras
BuildRequires: %{?scl_prefix}eclipse-pde >= 1:4.3.0
BuildRequires: %{?scl_prefix}eclipse-rse >= 3.4
BuildRequires: %{?scl_prefix}eclipse-remote
BuildRequires: %{?scl_prefix}eclipse-license
BuildRequires: %{?scl_prefix_java_common}maven-local
BuildRequires: desktop-file-utils
BuildRequires: %{?scl_prefix}lpg-java-compat
BuildRequires: %{?scl_prefix}eclipse-platform >= 1:4.3.0
BuildRequires: %{?scl_prefix}eclipse-tests >= 1:4.3.0
BuildRequires: %{?scl_prefix}eclipse-swtbot
BuildRequires: %{?scl_prefix}nekohtml
BuildRequires: %{?scl_prefix_maven}exec-maven-plugin

Requires:      %{?scl_prefix}gdb make %{?scl_prefix}gcc-c++ autoconf automake libtool
Requires:      %{?scl_prefix}eclipse-platform >= 1:4.3.0
Requires:      %{?scl_prefix}eclipse-rse >= 3.4
Requires:      %{?scl_prefix}eclipse-remote
Requires:      %{?scl_prefix}nekohtml
Requires:      %{?scl_prefix_java_common}xerces-j2
Requires:      %{?scl_prefix_java_common}xalan-j2
Requires:      %{?scl_prefix_java_common}xml-commons-resolver

%description
Eclipse features and plugins that are useful for C and C++ development.

%package parsers
Summary:        Eclipse C/C++ Development Tools (CDT) Optional Parsers
Group:          Text Editors/Integrated Development Environments (IDE)
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       %{?scl_prefix}lpg-java-compat

%description parsers
Optional language-variant parsers for the CDT.

%package tests
Summary:	Eclipse C/C++ Development Tools (CDT) Tests
Group:          Text Editors/Integrated Development Environments (IDE)
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       %{name}-parsers = %{epoch}:%{version}-%{release}
Requires:       %{?scl_prefix}eclipse-tests

%description tests
Test plugins for the CDT.

%package sdk
Summary:        Eclipse C/C++ Development Tools (CDT) SDK plugin
Group:          Text Editors/Integrated Development Environments (IDE)
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description sdk
Source for Eclipse CDT for use within Eclipse.

%prep
%setup -q -c

# get desktop info
mkdir desktop
cp %{SOURCE3} desktop

# handle man page
mkdir man
cp %{SOURCE4} man

pushd %{cdt_snapshot}
%patch0 -p1
%patch4 -p1
%patch5 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
sed -i -e 's/<arch>x86<\/arch>/<arch>%{eclipse_arch}<\/arch>/g' pom.xml
# Add secondary arch support if we are building there
%ifarch %{arm} s390 s390x aarch64
pushd core
pushd org.eclipse.cdt.core.native
sed -i -e 's/linux.x86 /linux.%{eclipse_arch} /g' plugin.properties
sed -i -e 's/\\(x86\\)/(%{eclipse_arch})/g' plugin.properties
popd
cp -r org.eclipse.cdt.core.linux.x86 org.eclipse.cdt.core.linux.%{eclipse_arch}
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
sed -i -e"/<module>core\/org.eclipse.cdt.core.linux.x86<\/module>/ a\ \t\t<module>core\/org.eclipse.cdt.core.linux.%{eclipse_arch}<\/module>" pom.xml
%endif
# Force the linux arch-specific plug-in to be a dir so that the .so files aren't loaded into
# the user.home .eclipse configuration
pushd core/org.eclipse.cdt.core.linux.%{eclipse_arch}
sed -i -e"/Bundle-Localization: plugin/ aEclipse-BundleShape: dir" META-INF/MANIFEST.MF
popd

%{?scl:scl enable %{scl_maven} %{scl} - <<"EOF"}
# Disable the jgit provider and force default packaging
%pom_remove_plugin org.eclipse.tycho:tycho-packaging-plugin
%{?scl:EOF}

popd

## Libhover stuff
tar -xaf %{SOURCE1}
pushd %{linuxtools_snapshot}

%patch1 -p0
%patch2 -p0
%patch3 -p0
%patch6 -p0

%{?scl:scl enable %{scl_maven} %{scl} - <<"EOF"}
%pom_remove_plugin org.jacoco:jacoco-maven-plugin
%pom_disable_module changelog
%pom_disable_module profiling
%pom_disable_module lttng
%pom_disable_module valgrind
%pom_disable_module gcov
%pom_disable_module gprof
%pom_disable_module oprofile
%pom_disable_module systemtap
%pom_disable_module perf
%pom_disable_module rpm
%pom_disable_module man

# Don't use target platform
%pom_disable_module org.eclipse.linuxtools.target releng
sed -i '/<target>/,/<\/target>/ d' pom.xml

# Newlib libhover is optional and we don't need it
%pom_disable_module org.eclipse.linuxtools.cdt.libhover.newlib libhover
%pom_disable_module org.eclipse.linuxtools.cdt.libhover.newlib-feature libhover
%pom_disable_module org.eclipse.linuxtools.cdt.libhover.tests libhover
%{?scl:EOF}

pushd libhover/org.eclipse.linuxtools.cdt.libhover.libstdcxx
mkdir data
cp %{SOURCE7} data/.
popd
popd

%build
export JAVA_HOME=/usr/lib/jvm/java

# Exclude EquinoxResolver to avoid NPE occuring on arm
%ifarch %{arm}
export MAVEN_OPTS="-XX:CompileCommand=exclude,org/eclipse/tycho/core/osgitools/EquinoxResolver,newState"
%endif

mkdir SDK
SDK=$(cd SDK >/dev/null && pwd)

#pushd %{cdt_snapshot}
#sed -i -e "s:/builddir/build/BUILD/myrepo:$repodir:g" pom.xml
#popd

mkdir home
homedir=$(cd home > /dev/null && pwd)

pushd %{cdt_snapshot}
pushd core/org.eclipse.cdt.core.linux/library
make JAVA_HOME="/usr/lib/jvm/java" ARCH=%{eclipse_arch} CC='gcc -D_GNU_SOURCE'
popd

%{?scl:scl enable %{scl_maven} %{scl} - <<"EOF"}
xmvn -o -Dtycho.local.keepTarget -Dskip-ppc64le -Dmaven.test.skip=true -Dmaven.repo.local=`pwd`/.m2 install
%{?scl:EOF}

## Libhover has dependencies on CDT so we must add these to the SDK directory
unzip -o releng/org.eclipse.cdt.repo/target/org.eclipse.cdt.repo.zip -d $SDK
popd

## Libhover build
pushd %{linuxtools_snapshot}

%{?scl:scl enable %{scl_maven} %{scl} - <<"EOF"}
xmvn -o -Dmaven.test.skip=true -Dmaven.repo.local=../%{cdt_snapshot}/.m2 -fae clean install
%{?scl:EOF}

pushd releng/org.eclipse.linuxtools.releng-site/target/repository/features
for f in `ls -1 . | grep jar$`; do
    unzip $f -d ${f/.jar//};
    rm -fr $f
done

popd

%install
# Eclipse may try to write to the home directory.
mkdir -p home
homedir=$(cd home > /dev/null && pwd)


installDir=${RPM_BUILD_ROOT}/%{eclipse_base}/dropins/cdt
testInstallDir=${RPM_BUILD_ROOT}/%{_javadir}/eclipse-cdt-tests/plugins
parsersInstallDir=${installDir}-parsers
sdkInstallDir=${installDir}-sdk
binInstallDir=${RPM_BUILD_ROOT}/%{_bindir}
manInstallDir=${RPM_BUILD_ROOT}/%{_mandir}/man1
install -d -m755 $installDir
install -d -m755 $parsersInstallDir
install -d -m755 $sdkInstallDir
install -d -m755 $testInstallDir
install -d -m755 $binInstallDir
install -d -m755 $manInstallDir

# Unzip contents of the cdt repo, removing all but plugins and features
unzip -q -o %{cdt_snapshot}/releng/org.eclipse.cdt.repo/target/org.eclipse.cdt.repo.zip \
-d $installDir/eclipse

#tests
# We need grep to return non-zero status to skip all non eclipse-test-plugins
pushd %{cdt_snapshot}
set +e
for pom in `find . -name pom.xml`; do
 grep -q '<packaging>eclipse-test-plugin</packaging>' ${pom}
 if [ $? -eq 0 ]; then
   testjar=`ls ${pom/pom.xml/}'target/'*.jar | grep -v sources`
   cp ${testjar} $testInstallDir
 fi
done
set -e
popd

# Libhover install
unzip -q -o %{linuxtools_snapshot}/releng/org.eclipse.linuxtools.releng-site/target/org.eclipse.linuxtools.releng-site.zip \
-d $installDir/eclipse

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
%{?scl: sed -i -e 's/Name=Eclipse/Name=DTS Eclipse/g' desktop/eclipse-cdt.desktop}
install -D desktop/eclipse-cdt.desktop $RPM_BUILD_ROOT/usr/share/applications/%{name}.desktop
desktop-file-validate $RPM_BUILD_ROOT/usr/share/applications/%{name}.desktop

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

pushd $installDir/eclipse/plugins
XERCES_JAR=`ls org.apache.xerces*`
CYBERNEKO_JAR=`ls org.cyberneko.html*`
rm $XERCES_JAR
rm $CYBERNEKO_JAR
ln -s %{_javadir}/nekohtml.jar $CYBERNEKO_JAR
ln -s %{_javadir_java_common}/xerces-j2.jar $XERCES_JAR
ln -s %{_javadir_java_common}/xalan-j2-serializer.jar org.apache.xml.serializer.jar
ln -s %{_javadir_java_common}/xml-commons-resolver.jar org.apache.xml.resolver.jar
popd

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
/usr/share/applications/*
%{_mandir}/man1/cdtdebug.1*
%doc %{cdt_snapshot}/releng/org.eclipse.cdt.releng/epl-v10.html
%doc %{cdt_snapshot}/releng/org.eclipse.cdt.releng/notice.html

%files sdk
%{eclipse_base}/dropins/cdt-sdk
%doc %{cdt_snapshot}/releng/org.eclipse.cdt.releng/epl-v10.html
%doc %{cdt_snapshot}/releng/org.eclipse.cdt.releng/notice.html

%files parsers
%{eclipse_base}/dropins/cdt-parsers
%doc %{cdt_snapshot}/releng/org.eclipse.cdt.releng/epl-v10.html
%doc %{cdt_snapshot}/releng/org.eclipse.cdt.releng/notice.html

%files tests
%{_javadir}/eclipse-cdt-tests
%doc %{cdt_snapshot}/releng/org.eclipse.cdt.releng/epl-v10.html
%doc %{cdt_snapshot}/releng/org.eclipse.cdt.releng/notice.html

%changelog
* Thu Feb 26 2015 Roland Grunberg <rgrunber@redhat.com> - 1:8.6.0-1
- Update to Luna SR2 release 8.6.0.
- Resolves: rhbz#1175107.

* Sun Jan 25 2015 Mat Booth <mat.booth@redhat.com> - 1:8.5.0-11
- Resolves: rhbz#1185541 - Symlink to java-common versions of deps

* Thu Jan 22 2015 Mat Booth <mat.booth@redhat.com> - 1:8.5.0-10
- Resolves: rhbz#1184737 - Fix launcher for standalone debugger
- Resolves: rhbz#1184734 - Fix incorrect working dir prefixes

* Mon Jan 19 2015 Mat Booth <mat.booth@redhat.com> - 1:8.5.0-9
- Disable unsupported llvm subpackage

* Fri Jan 16 2015 Mat Booth <mat.booth@redhat.com> - 1:8.5.0-8
- Revert usage of nekohtml from rh-java-common for now

* Fri Jan 16 2015 Mat Booth <mat.booth@redhat.com> - 1:8.5.0-7
- Migrate to rh-java-common version of nekohtml
- Fix link to lpg

* Thu Jan 15 2015 Roland Grunberg <rgrunber@redhat.com> - 1:8.5.0-6
- Fix dependencies on subpackages.

* Thu Jan 15 2015 Roland Grunberg <rgrunber@redhat.com> - 1:8.5.0-5
- Generate auto-provides/requires.

* Tue Jan 13 2015 Roland Grunberg <rgrunber@redhat.com> - 1:8.5.0-4
- Minor changes to build SCL-ized.
- Resolves: rhbz#1175105

* Thu Oct 09 2014 Mat Booth <mat.booth@redhat.com> - 1:8.5.0-3
- Update libhover
- Prefer macro usage instead of patching poms
- Organise patches

* Tue Oct 07 2014 Jeff Johnston <jjohnstn@redhat.com> - 1:8.5.0-2
- Remove experimental launchbar feature and tests.

* Mon Oct 06 2014 Mat Booth <mat.booth@redhat.com> - 1:8.5.0-1
- Update to Luna SR1 release 8.5.0

* Thu Sep 04 2014 Roland Grunberg <rgrunber@redhat.com> - 1:8.4.0-6
- Remove unnecessary patch.

* Tue Aug 19 2014 Mat Booth <mat.booth@redhat.com> - 1:8.4.0-5
- Update dep on nekohtml to fix libhover generation error at startup

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:8.4.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jul 31 2014 Jeff Johnston <jjohnstn@redhat.com> 1:8.4.0-3
- Link org.apache.xml.resolver and org.apache.xml.serializer plugins from
  Fedora packages

* Thu Jul 10 2014 Jeff Johnston <jjohnstn@redhat.com> 1:8.4.0-2
- Update Stand-alone debugger support to include fixes, help
  support, and a man page

* Thu Jun 26 2014 Jeff Johnston <jjohnstn@redhat.com> 1:8.4.0-1
- Update to offical Luna CDT 8.4.0 and Linux Tools 3.0

* Wed Jun 25 2014 Alexander Kurtakov <akurtako@redhat.com> 1:8.4.0-0.7.git20140506
- Drop the ExclusiveArch it only complicates things and is growing too big with ppc64le and aarch64 to be added.

* Thu Jun 19 2014 Jeff Johnston <jjohnstn@redhat.com>  1:8.4.0-0.6.git20140506
- Add desktop integration for standalone debugger executable

* Fri Jun 13 2014 Jeff Johnston <jjohnstn@redhat.com>  1:8.4.0-0.5.git20140506
- Add /usr/bin/cdtdebug binary
- Fix cdtdebug config.ini to have full paths to dropins plugins
- Remove org.eclipse.cdt.core.tests from being shipped in base package
- Add Requires for eclipse-remote

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:8.4.0-0.4.git20140506
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu May 22 2014 Alexander Kurtakov <akurtako@redhat.com> 1:8.4.0-0.3.git20140506
- Use xmvn to build.

* Thu May 15 2014 Jeff Johnston <jjohnstn@redhat.com> 1:8.4.0-0.2.git20140506
- Remove org.apache.xerces and org.cyberneko.html plugins from installation
  and link to jars from Fedora packages

* Tue May 13 2014 Jeff Johnston <jjohnstn@redhat.com> 1:8.4.0-0.1.git20140506
- Update CDT to 8.4.0 Luna M7 build
- Update Libhover to Linux Tools 3.0 Luna M7 build

* Wed Mar 05 2014 Jeff Johnston <jjohnstn@redhat.com> 1:8.3.0-1
- Update CDT to 8.3.0 (Kepler SR2)
- Update Libhover to Linux Tools 2.2.1 (Kepler SR2)

* Tue Oct 08 2013 Jeff Johnston <jjohnstn@redhat.com> 1:8.2.1-3
- Add eclipse-tests as requirement of eclipse-cdt-tests package.

* Mon Oct 07 2013 Jeff Johnston <jjohnstn@redhat.com> 1:8.2.1-2
- Add eclipse-cdt-tests sub-package
- Add patch to fix autotools tests build properties

* Mon Sep 30 2013 Jeff Johnston <jjohnstn@redhat.com> 1:8.2.1-1
- Update CDT to 8.2.1 (Kepler SR1)
- Update Libhover to Linux Tools 2.1.0 (Kepler SR1)

* Thu Aug 22 2013 Jeff Johnston <jjohnstn@redhat.com> 1:8.2.0-3
- Fix Indexer preferences page
- Resolves: #966960

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:8.2.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jul 1 2013 Alexander Kurtakov <akurtako@redhat.com> 1:8.2.0-1
- Update to Kepler final.
- Don't force qualifiers.

* Fri Jun 07 2013 Roland Grunberg <rgrunber@redhat.com> 1:8.2.0-0.8.rc3
- Update CDT to Kepler RC3.

* Thu May 30 2013 Jeff Johnston <jjohnstn@redhat.com> 1:8.2.0-0.7.rc2
- Update CDT to Kepler RC2.

* Fri May 10 2013 Jeff Johnston <jjohnstn@redhat.com> 1:8.2.0-0.6.m7
- Update CDT to Kepler M7.

* Wed May 08 2013 Jeff Johnston <jjohnstn@redhat.com> 1:8.2.0-0.5.m6
- Fix bug 407580 regarding building autotools projects with GnuMakefiles

* Tue Apr 30 2013 Alexander Kurtakov <akurtako@redhat.com> 1:8.2.0-0.4.m6
- Remove trace-back when spawner library is not found.
- Fix libhover source plugin generation.
- Add fix for bug 405904 concerning gprof link options.

* Tue Apr 23 2013 Alexander Kurtakov <akurtako@redhat.com> 1:8.2.0-0.3.m6
- llvm subpackage without clang is useless.

* Wed Apr 10 2013 Jeff Johnston <jjohnstn@redhat.com> - 1:8.2.0-0.1.m6
- Update CDT to Kepler M6.
- Update libhover to Kepler M6 and use tycho to build it now.
- Add new llvm subpackage.

* Fri Mar 08 2013 Jeff Johnston <jjohnstn@redhat.com> - 1:8.1.2-1
- Update CDT to Juno SR2 (8.1.2)
- Update libhover to Juno SR2 (1.2.1)

* Wed Mar 06 2013 Jeff Johnston <jjohnstn@redhat.com> - 1:8.1.1-5
- Fix summary for parsers sub-package.
- Patch CDT dsf tests to not require junit4.

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 1:8.1.1-4
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Mon Jan 28 2013 Jeff Johnston <jjohnstn@redhat.com> - 1:8.1.1-3
- Force org.eclipse.cdt.linux.%%{arch} to be a dir so that the .so files
  are not loaded into the user's .eclipse configuration.

* Fri Jan 25 2013 Jeff Johnston <jjohnstn@redhat.com> - 1:8.1.1-2
- Add compiler exclusion to prevent NPE occuring for arm build.

* Thu Oct 11 2012 Jeff Johnston <jjohnstn@redhat.com> - 1:8.1.1-1
- Update CDT to 8.1.1 (Juno SR1)
- Update Libhover to 1.1.1 (Juno SR1)

* Wed Oct 03 2012 Jeff Johnston <jjohnstn@redhat.com> - 1:8.1.0-3
- Remove unneeded objectweb-asm dependency.
- Add special flags so build will work with tycho 0.16.
- Fix up zip file name since tycho 0.16 changed it.

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:8.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jul 03 2012 Jeff Johnston <jjohnstn@redhat.com> 1:8.1.0-1
- Update CDT to official Juno 8.1.0 release.
- Update libhover to Linux Tools 1.0.0 release.

* Thu Jun 14 2012 Roland Grunberg <rgrunber@redhat.com> 1:8.1.0-0.11.junom7
- Remove patches that bump BREE to JavaSE-1.6 (done by Tycho)
- Remove patch and %%prep lines that create local p2 repository (done by Tycho)

* Wed May 16 2012 Jeff Johnston <jjohnstn@redhat.com> 1:8.1.0-0.10.junom7
- Update CDT to Juno M7 (8.1.0 pre-release).

* Mon May 07 2012 Dan Horák <dan[at]danny.cz> 1:8.1.0-0.9.junom6
- Use %%{eclipse_arch} where possible and make it work on all secondary arches

* Mon May 07 2012 Jeff Johnston <jjohnstn@redhat.com> 1:8.1.0-0.8.junom6
- Fix arm build so that the arm fragment for CDT core gets built.

* Thu May 03 2012 Dan Horák <dan[at]danny.cz> 1:8.1.0-0.7.junom6
- Enable build on s390(x).

* Mon Apr 23 2012 Jeff Johnston <jjohnstn@redhat.com> 1:8.1.0-0.6.junom6
- Add arm build support.
- Resolves: #815969 - Libhover not working for Juno M6 build 0.4.

* Fri Apr 20 2012 Jeff Johnston <jjohnstn@redhat.com> 1:8.1.0-0.5.junom6
- Remove P2 generation section that is no longer needed.
- Add libhover.devhelp feature.
- Remove net.sourceforge.lpg.lpgjavaruntime.jar and only use link.
- Add org.eclipse.cdt.core.tests jar.

* Thu Apr 19 2012 Jeff Johnston <jjohnstn@redhat.com> 1:8.1.0-0.4.junom6
- Clear out repo files that are added to the dropin folder.
- Add doc files per standard method.

* Wed Apr 18 2012 Jeff Johnston <jjohnstn@redhat.com> 1:8.1.0-0.3.junom6
- Fix context qualifiers to match upstream CDT and Libhover.

* Wed Apr 18 2012 Alexander Kurtakov <akurtako@redhat.com> 1:8.1.0-0.2.junom6
- Remove unneeded cleanups.
- Organize patches.
- Use the official libhover tarball.
- Build using pdebuild script.

* Tue Apr 17 2012 Jeff Johnston <jjohnstn@redhat.com> 1:8.1.0-0.1.junom6
- Update CDT to Juno M6 (8.1.0 pre-release).
- Switch to use tycho to build CDT.
- Remove autotools build since it is now part of CDT.
- Update libhover to Linux Tools 0.10.0 version.

* Tue Feb 14 2012 Sami Wagiaalla <swagiaal@redhat.com> 1:8.0.1-4
- Remove calls to reconciler.

* Wed Feb 01 2012 Jeff Johnston <jjohnstn@redhat.com> 1:8.0.1-4
- Change launcher main class to be org.eclipse.equinox.launcher.Main
- Remove java compile exclusions
- Add main as target for ant builds for Autotools and Libhover

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:8.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Nov 28 2011 Jeff Johnston <jjohnstn@redhat.com> 1:8.0.1-2
- Add arch filtering for rhel
- Remove extraneous echo statement

* Mon Nov 07 2011 Jeff Johnston <jjohnstn@redhat.com> 1:8.0.1-1
- Rebase CDT to 8.0.1
- Rebase Libhover and Autotools to 0.9 versions
- Account for new CDT repository structure

* Wed Oct 5 2011 Sami Wagiaalla <swagiaal@redhat.com> 1:8.0.0-6
- Depend on a specific release of eclipse-platform.

* Wed Oct 5 2011 Sami Wagiaalla <swagiaal@redhat.com> 1:8.0.0-6
- Use the reconciler to install/uninstall plugins during rpm
  post and postun respectively.

* Mon Jul 25 2011 Jeff Johnston <jjohnstn@redhat.com> 1:8.0.0-5
- Additional patch for https://bugs.eclipse.org/bugs/show_bug.cgi?id=351660

* Thu Jul 21 2011 Jeff Johnston <jjohnstn@redhat.com> 1:8.0.0-4
- Patch for https://bugs.eclipse.org/bugs/show_bug.cgi?id=351660

* Fri Jul 15 2011 Sami Wagiaalla <swagiaal@redhat.com> 1:8.0.0-3
- Added patch for https://bugs.eclipse.org/bugs/show_bug.cgi?id=352166

* Mon Jun 27 2011 Jeff Johnston  <jjohnstn@redhat.com> 1:8.0.0-2
- Fix RSE requires.

* Thu Jun 23 2011 Jeff Johnston  <jjohnstn@redhat.com> 1:8.0.0-1
- Rebase CDT to 8.0.0
- Rebase Libhover and Autotools to 0.8 versions
- Use org.eclipse.equinox.p2.publisher.EclipseGenerator
- Switch to use org.eclipse.equinox.launcher instead of startup.jar
- Use Eclipse 3.7
 
* Wed Feb 16 2011 Jeff Johnston  <jjohnstn@redhat.com> 1:7.0.1-5
- Add additional patch so glibc and libstdc++ libhover plug-ins reference
  local location for their libhover data.

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:7.0.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Jan 05 2011 Jeff Johnston  <jjohnstn@redhat.com> 1:7.0.1-3
- Add patch for Eclipse bug 286162.

* Thu Oct 07 2010 Jeff Johnston  <jjohnstn@redhat.com> 1:7.0.1-2
- Rebase CDT to Helios SR1 (7.0.1) including gdb hardware support
- Rebase Autotools/Libhover to Linux tools R0.6.1

* Wed Jul 14 2010 Jeff Johnston  <jjohnstn@redhat.com> 1:7.0.0-1
- Rebase CDT to Helios (7.0.0)
- Rebase Autotools/Libhover to Linux tools R0.6.0

* Tue May 18 2010 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.2-5
- Rebase Autotools/Libhover to Linux tools R0.5.1.
- Remove addbuilder patch which is already part of R0_5_1.
- Remove libhover template patch which is already part of R0_5_1.

* Thu May 06 2010 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.2-4
- Add libtool as a requirement.

* Fri Mar 19 2010 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.2-3
- Fix autotools local patch to add macros directory to build.properties
  of org.eclipse.linuxtools.cdt.autotools.core.

* Fri Mar 19 2010 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.2-2
- Check in missing maketargets patch.

* Thu Mar 18 2010 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.2-1
- Rebase CDT to Galileo SR2 (6.0.2).
- Rebase Autotools to Linux tools R0.5.
- Rebase Libhover to Linux tools R0.5.

* Fri Jan 29 2010 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.1-8
- Fix urls for autotools and libhover sources.
- Add source references for autotools and libhover fetch scripts.

* Fri Dec 11 2009 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.1-7
- Rebase Autotools to Linux tools 0.4.0.1 release.
- Rebase Libhover to Linux tools 0.4.0 release.
- Remove libhover patch which is now part of rebase.

* Wed Oct 28 2009 Alexander Kurtakov <akurtako@redhat.com> 1:6.0.1-6
- Disable mylyn bridge build, part of eclipse-mylyn srpm now.

* Tue Oct 27 2009 Alexander Kurtakov <akurtako@redhat.com> 1:6.0.1-5
- Sync build_id with upstream 6.0.1.

* Fri Oct 16 2009 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.1-4
- Rebase Autotools to 1.0.5.
- Add patch to move macro hover docs locally into Autotools plugin.

* Thu Oct 15 2009 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.1-3
- Include installed link for lpg java bundle in new cdt-parsers subpackage.

* Wed Oct 14 2009 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.1-2
- Ship new parsers sub-package which includes xlc, upc, and lrparser plug-ins.
- Require lpg-java-compat for build.

* Fri Oct 09 2009 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.1-1
- Rebase CDT to 6.0.1.

* Mon Oct 05 2009 Andrew Overholt <overholt@redhat.com> 1:6.0.0-11
- Build on ppc64

* Wed Sep 23 2009 Jeff Johnston <jjohnstn@redhat.com> 1:6.0.0-10
- Resolves #290247
- Upgrade libhover to 0.3.0.
- Add libhover patch to fix libstdc++ member resolution and
  to place libhover docs locally within libhover plugin.

* Wed Aug 12 2009 Andrew Overholt <overholt@redhat.com> 1:6.0.0-9
- Use launcher jar to run metadata generator instead of eclipse binary.

* Wed Aug 12 2009 Andrew Overholt <overholt@redhat.com> 1:6.0.0-8
- Remove shipping of content.xml.

* Wed Jul 29 2009 Jeff Johnston <jjohnstn@redhat.com> 1:6.0.0-7
- Resolves #514629

* Mon Jul 27 2009 Jeff Johnston <jjohnstn@redhat.com> 1:6.0.0-6
- Remove gcj_support.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:6.0.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jul 24 2009 Jeff Johnston <jjohnstn@redhat.com> 6.0.0-3
- Bump release number.
- Update Autotools to v200907241319 which has CDT 6.0 fixes.

* Wed Jun 17 2009 Jeff Johnston <jjohnstn@redhat.com> 6.0.0-1
- Rebase CDT to 6.0.0.
- Rebase Autotools to v200906171600 snapshot.
- Resolves #280504, #280505, #280506, #280509.

* Mon Jun 15 2009 Jeff Johnston <jjohnstn@redhat.com> 5.0.2-3
- Resolves #280117.

* Wed Apr 08 2009 Jeff Johnston <jjohnstn@redhat.com> 5.0.2-2
- Bump release.

* Tue Apr 07 2009 Jeff Johnston <jjohnstn@redhat.com> 5.0.2-1
- Rebase autotools to 1.0.3.
- Rebase CDT to v200903191301 (5.0.2).

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:5.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Jan 16 2009 Jeff Johnston <jjohnstn@redhat.com> 5.0.1-2
- Rebase libhover to 0.1.1 and autotools to 1.0.2.
- Remove patch for 472731 which is already part of rebased autotools sources.

* Fri Nov 28 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.1-1
- Rebase to CDT 5.0.1.
- Fix bug in autotools project type detection.
- Resolve #472731

* Mon Nov 17 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-12
- Fix typo in autotools and libhover sources tarballs.
- Remove redundant patches which are already in new tarballs.

* Thu Nov 06 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-11
- Fix managed configurations dialog problem.
- Update libhover and autotools source tarballs to 20081106 snapshot.

* Thu Oct 16 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-10
- Change runtests section to remove new libhover plugin rather than old
  com.redhat.* autotools plugin.

* Thu Oct 16 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-9
- Fix org.eclipse.linuxtools.libhover.glibc plugin to add toc.xml to
  binary file list.

* Thu Oct 16 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-8
- Fix org.eclipse.linuxtools.libhover.feature to include
  org.eclipse.linuxtools.libhover.library_docs plugin.
- Add work-around patch for managed configurations dialog problem.

* Wed Oct 15 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-7
- Change to use new linuxtools version of autotools-1.0.1.
- Add build of libhover plugins again from linuxtools.

* Tue Sep 09 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-6
- Fix for NPE during alteration of Autotools configuration settings.
- Resolves #461647

* Thu Sep 04 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-5
- Fix for autotools plugin referencing invalid build nature.
- Resolves #461201

* Wed Aug 20 2008 Andrew Overholt <overholt@redhat.com> 5.0.0-4
- Add building and running of tests
- Remove LexerTests until 5.0.1
- Fix fetch script to use new location of PDE Build

* Mon Aug 11 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-3
- Fix build id to be 200806171202.

* Fri Aug 08 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-2
- Add autotools 1.0.0 which supports CDT 5.0.
- Use java -cp to build cdt and autotools instead of eclipse -nosplash.
- Replace fetched source with CDT_5_0_0 tagged sources.

* Wed Aug 06 2008 Andrew Overholt <overholt@redhat.com> 5.0.0-1
- Remove master and testing features
- Move files to dropins/cdt{,-mylyn,-sdk}/eclipse
- Generate p2 metadata

* Fri Aug 01 2008 Andrew Overholt <overholt@redhat.com> 5.0.0-1
- 5.0
- Add Mylyn sub-package
- Disable CPPUnit for now
- Disable autotools until a new snapshot is made that will build with 5.0

* Thu Jul 17 2008 Tom "spot" Callaway <tcallawa@redhat.com> 4.0.3-2
- fix license tag

* Fri Apr 04 2008 Jeff Johnston <jjohnstn@redhat.com> 4.0.3-1
- Rebase to CDT 4.0.3
- Patch openpty code to not reference stropts.h which is no longer shipped
- Update eclipse-cdt-no-tests.patch

* Mon Jan 28 2008 Jeff Johnston <jjohnstn@redhat.com> 4.0.1-4
- Update autotools to 0.9.6
- Includes generic shell script support for makefile generation on
  different platforms

* Wed Dec 05 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.1-3
- Resolves #412651, #412661, #385991 
- Rebase autotools to 0.9.5.3
- Adds glibc C library completion support.
- Fix clean by removal option.
- Add support for changes to configure/autogen command names.
- Add gcj checks for %%post and %%postun steps.

* Wed Oct 24 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.1-2
- Rebase autotools to 0.9.5.1
- Add autotools property tab for C/C++ build.
- Resolves #330701

* Thu Oct 04 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.1-1
- Use official CDT 4.0.1 source tarball
- Update autotools to 0.9.5
- Resolves #315811

* Tue Sep 25 2007 Andrew Overholt <overholt@redhat.com> 4.0.1-0.2.v200709241202cvs
- Fix moving of arch-specific plugins that haven't been updated to new
  version.

* Mon Sep 24 2007 Andrew Overholt <overholt@redhat.com> 4.0.1-0.1.v200709241202cvs
- 4.0.1 RC.
- Update autotools for Binaries fix.

* Thu Sep 13 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.0-7
- Resolves #288711
- Ensure that all features are unpacked.

* Mon Sep 10 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.0-6
- Resolves #274551, #253331, #254246, #254248
- Rebase Autotools to 0.9.3 

* Thu Aug 23 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.0-5
- Add eclipse-cvs-client dependency

* Fri Aug 17 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.0-4
- Fix release number in Autotools feature to be 0.9.2.

* Thu Aug 16 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.0-3
- Resolves #251412
- Rebase autotools to 0.9.2
- Add minimum java runtime requirement
- Add direct Autotools wizards
- Add autogen.sh options

* Fri Aug 10 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.0-2
- Add Epoch 1 back.

* Wed Aug 08 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.0-1
- Rebase to CDT 4.0.0
- Rebase Autotools to 0.9.1

* Mon Apr 16 2007 Jeff Johnston <jjohnstn@redhat.com> 3.1.2-3
- Add missing gif to org.eclipse.cdt.make.ui.
- Resolves: #236558

* Tue Feb 27 2007 Jeff Johnston <jjohnstn@redhat.com> 3.1.2-2
- Resolves: #229891, #230253, #205310, #229893
- Rebase autotools to 0.0.8.1 source.

* Wed Feb 21 2007 Jeff Johnston <jjohnstn@redhat.com> 3.1.2-1
- Rebase CDT to 3.1.2.
- Rebase autotools to 0.0.8 source.
- Replace subconsole patch with new build console patch.

* Mon Jan 29 2007 Jeff Johnston <jjohnstn@redhat.com> 3.1.1-8
- Resolves: #214624, #224644
- Rebase autotools to 0.0.7 source.

* Wed Jan 17 2007 Jeff Johnston <jjohnstn@redhat.com> 3.1.1-7
- Resolves: #222350
- Rebase autotools to 0.0.6.1 source.
- Add comments.
- Put arch-specific jars in library dir.

* Mon Dec 11 2006 Jeff Johnston <jjohnstn@redhat.com> 3.1.1-6
- Rebase autotools to 0.0.6 source.

* Wed Nov 15 2006 Jeff Johnston <jjohnstn@redhat.com> 3.1.1-5
- Add cppunit support.

* Mon Nov 06 2006 Andrew Overholt <overholt@redhat.com> 3.1.1-4
- Use the new location of copy-platform.

* Thu Oct 19 2006 Ben Konrath <bkonrath@redhat.com> 3.1.1-3
- Remove work-around for gcc bug # 20198.
- Do not include notice.html and epl-v10.html because these files are already
  included in the SDK.
- Put JNI libraries in %%{_libdir}/eclipse.
- Only build the CDT SDK.
- Fix build issue on non-x86 systems.
- Resolves: #208622

* Mon Oct 16 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.1-2
- Replace build patches with sed commands
- Resolves: #208622

* Mon Oct 16 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.1-2
- Fix build so only single platform is built at a time
- Bugzilla 208622

* Thu Sep 28 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.1-1
- Rebase autotools to 0.0.5 source.
- Rebase CDT to 3.1.1 source.
- Bugzilla 206719, 206359, 206164

* Mon Sep 11 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-3
- Add hover help for defined symbols
- Fix bug with defined symbol calculation on file that compilation
  string cannot be fetched for

* Fri Sep 01 2006 Ben Konrath <bkonrath@redhat.com> 3.1.0-2
- Remove jpp in release.
- Require java-gcj-compat >= 1.0.64.

* Tue Aug 29 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_13fc
- Rebase autotools to 0.0.4 source.
- Use ScannerInfoProvider extension instead of DynamicScannerInfoProvider.
- Add sub-console support to CDT.

* Mon Aug 21 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_12fc
- Fix build special targets when project hasn't configured yet.
- Fix to fully reconfigure after configuration options change.
- Fix configuration problem whereby config.sub complains.
- Bugzilla 200000, 201270, 203440

* Tue Aug 08 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_11fc
- Fix Build Special Targets bug when importing a CVS project and
  using ManagedMake Project Wizard.
- Bugzilla 201269

* Mon Jul 31 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_10fc
- Fix bug with library hover help.

* Tue Jul 25 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_9fc
- Remove redundant runtime packages from sdk.

* Tue Jul 25 2006 Ben Konrath <bkonrath@redhat.com> 3.1.0-1jpp_8fc
- Add epoch to sdk requires.

* Mon Jul 24 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_8fc
- Update autotools sources.
- Rebuild.

* Mon Jul 24 2006 Ben Konrath <bkonrath@redhat.com> 3.1.0-1jpp_7fc
- Rebuld.

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> 3.1.0-1jpp_6fc
- Rebuilt

* Thu Jul 20 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_5fc
- Split into main package and sdk sub-package.

* Thu Jul 20 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_4fc
- Add Autotools plug-ins via additional source tarball.

* Wed Jul 19 2006 Igor Foox  <ifoox@redhat.com> 3.1.0-1jpp_3fc
- Rebuild.

* Wed Jul 12 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_2fc
- Add dynamic scannerinfo extension used by Autotools plug-in.

* Mon Jul 10 2006 Andrew Overholt <overholt@redhat.com> 3.1.0-1jpp_1fc
- 3.1.0.

* Thu Jun 08 2006 Andrew Overholt <overholt@redhat.com> 3.1.0-0jpp_0fc.3.1.0RC2 
- 3.1.0 RC2.
- Remove unused hover patch.
- Use newly-created versionless pde.build symlink.
- Remove no-sdkbuild patch.

* Mon Apr 03 2006 Andrew Overholt <overholt@redhat.com> 3.0.2-1jpp_3fc
- Add ia64.

* Tue Mar 07 2006 Andrew Overholt <overholt@redhat.com> 3.0.2-1jpp_2fc
- Bump release.

* Mon Feb 13 2006 Andrew Overholt <overholt@redhat.com> 3.0.2-1jpp_1fc
- 3.0.2.

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1:3.0.1-1jpp_8fc
- bump again for double-long bug on ppc(64)

* Fri Feb 10 2006 Andrew Overholt <overholt@redhat.com> 3.0.1-1jpp_7fc
- Use Epoch in Requires (rh#180915).
- Require >= 3.1.2 but < 3.1.3 to ensure we get 3.1.2.

* Thu Feb 09 2006 Andrew Overholt <overholt@redhat.com> 3.0.1-1jpp_6fc
- Make it Require >= 3.1.2.

* Thu Feb 09 2006 Andrew Overholt <overholt@redhat.com> 3.0.1-1jpp_5fc
- Build against SDK 3.1.2.

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1:3.0.1-1jpp_5fc
- rebuilt for new gcc4.1 snapshot and glibc changes

* Tue Jan 10 2006 Andrew Overholt <overholt@redhat.com> 3.0.1-1jpp_4fc
- Rebuild against latest gcc.

* Fri Dec 30 2005 Andrew Overholt <overholt@redhat.com> 3.0.1-1jpp_3fc
- Fix %%files section to not be x86-specific.

* Fri Dec 16 2005 Andrew Overholt <overholt@redhat.com> 3.0.1-1jpp_2fc
- Build against gcc 4.1.

* Mon Nov 14 2005 Andrew Overholt <overholt@redhat.com> 3.0.1-1jpp_1fc
- 3.0.1.

* Fri Oct 21 2005 Andrew Overholt <overholt@redhat.com> 3.0.0_fc-2
- Rebuild against gcc 4.0.2

* Tue Aug 23 2005 Andrew Overholt <overholt@redhat.com> 3.0.0_fc-1
- Import new upstream version (3.0).

* Thu Jul 14 2005 Andrew Overholt <overholt@redhat.com> 3.0.0_fc-0.RC2.1
- Import new upstream version (3.0RC2).
- Use gbenson's new aot-compile-rpm and change requirements appropriately.
- Re-enable native compilation - let's see what happens.

* Wed Jun 22 2005 Andrew Overholt <overholt@redhat.com> 3.0.0_fc-0.M7.1
- Import new upstream version (3.0M7).
- Remove refactoring/build.properties patch (now unneeeded).

* Fri Jun 03 2005 Jeff Pound <jpound@redhat.com> 3.0.0_fc-0.M6.8
- Patch refactoring/build.properties to include plugin.properties.
- Temporarily move all *.so's to *.so.bak due to native compilation bug.
- Temporarily remove gcj .jar -> .so db population.

* Mon May 23 2005 Andrew Overholt <overholt@redhat.com> 3.0.0_fc-0.M6.7
- Bring in new I-build to enable jump to Eclipse 3.1M7 and fix some critical
  issues.

* Wed May 11 2005 Ben Konrath <bkonrath@redhat.com> 3.0.0_fc-0.M6.6
- Temporarily disable org.eclipse.cdt.managedbuilder.core_3.0.0/libmngbuildcore.jar.so.

* Wed Apr 27 2005 Phil Muldoon <pmuldoon@redhat.com> 3.0.0_fc-0.M6.5
- Changed to find-and-aot-compile build usage
- Added "if gcj_support" toggle
- Fixed installing all arch fragments (now only installs one (correct) arch)
- Redid BuildRequires and Requires to remove old/unneeded dependencies
- Cleaned %%eclipse_arch declares.

* Thu Apr 21 2005 Phil Muldoon <pmuldoon@redhat.com> 3.0.0_fc-0.M6.4
- Added Chris Moller's libhover patch

* Sat Apr 16 2005 Ben Konrath <bkonrath@redhat.com> 3.0.0_fc-0.M6.3
- Clean up spec file (remove references to old patches and rh docs).

* Fri Apr 15 2005 Phil Muldoon <pmuldoon@redhat.com> 3.0.0_fc-0.M6.2
- Generated tarball from official final tagged M6 build

* Mon Apr 11 2005 Phil Muldoon <pmuldoon@redhat.com> 3.0.0_fc-0.M6.1
- Fixed db path in java -cp
- Regenerated tarball from M6 canditate build
- Reworked patches for M6 canditate Build

* Thu Apr 07 2005 Phil Muldoon <pmuldoon@redhat.com> 3.0.0_fc-0.M5.4
- Changed Requires eclipse-ui to eclipse-platform
- Added Requires java-1.4.2-gcj-compat >= 1.4.2.0-40jpp_14rh
- Added Requires gcc-java >= 4.0.0-0.35

* Mon Apr 04 2005 Phil Muldoon <pmuldoon@redhat.com> 3.0.0_fc-0.M5.3
- Added eclipse-cdt-no-sdkbuild.patch to build for platform only (fc4 space crunch)

* Sun Apr 03 2005 Andrew Overholt <overholt@redhat.com> 3.0.0_fc-0.M5.2
- Make use of rebuild-gcj-db.
- Use system-wide classmap.db.

* Wed Mar 23 2005 Phil Muldoon <pmuldoon@redhat.com> 3.0.0-1
- Updated to upstream CDT 3.0.0 M5 sources
- Removed Source1 (rhdocs) for now
- Removed libhover patch until updated
- Added eclipse-cdt-platform-build-linux.patch
- Added eclipse-cdt-sdk-build-linux.patch
- Stopped tests build for now (Added eclipse-cdt-no-tests.patch)
- Added Requires gcc-java (bz# 151866)
- Added new central db logic

* Fri Mar 4 2005 Phil Muldoon <pmuldoon@redhat.com> 2.0.2-3
- Added x86_64 to ExclusiveArch

* Thu Mar 3 2005 Phil Muldoon <pmuldoon@redhat.com> 2.0.2-2
- Moved upstream sources back to 2.0.2
- Revered back to releng build
- Added native build sections to spec file

* Tue Jan 11 2005 Ben Konrath <bkonrath@redhat.com> 2.1.0-1
- add devel rpm and use the patched sources for it
- update sources to 2.1.0
- new build method that does not require pre-fetched sources

* Sun Nov 07 2004 Ben Konrath <bkonrath@redhat.com> 2.0.2-1
- Update sources to 2.0.2
- Change which files are unzipped in the install phase - this changed in 2.0.2
- Update Red Hat documentation sources
- Remove no-cvs-patch as it is no longer needed (no-cvs2-patch is still needed)
- Update ui-libhover-patch 
- Add how-to document for doc and source tarball generation
- Add fetch-tests-patch for tarball generation

* Mon Jul 26 2004 Jeremy Handcock <handcock@redhat.com> 2.0-11
- Update Red Hat documentation sources

* Fri Jul 23 2004 Tom Tromey <tromey@redhat.com> 2.0-10
- Set user.home on all java invocations

* Fri Jul 23 2004 Tom Tromey <tromey@redhat.com> 2.0-9
- Pass dontFetchAnything to the build

* Fri Jul 23 2004 Tom Tromey <tromey@redhat.com> 2.0-8
- Patch from Phil Muldoon to avoid cvs operations

* Fri Jul 23 2004 Jeremy Handcock <handcock@redhat.com> 2.0-7
- Don't build on ppc64
- Require eclipse-ui, not eclipse-platform

* Fri Jul 23 2004 Tom Tromey <tromey@redhat.com> 2.0-6
- Set user.home when building

* Wed Jul 21 2004 Tom Tromey <tromey@redhat.com> 2.0-5
- Make .so files executable

* Wed Jul 21 2004 Chris Moller <cmoller@redhat.com> 2.0-4
- Add texthover

* Tue Jul 20 2004 Jeremy Handcock <handcock@redhat.com> 2.0-4
- Update Red Hat documentation sources

* Fri Jul 16 2004 Tom Tromey <tromey@redhat.com> 2.0-3
- Make platform symlink tree before building

* Fri Jul 16 2004 Jeremy Handcock <handcock@redhat.com> 2.0-3
- Add Red Hat-specific documentation
- Use `name' macro in source and patch names
- Correct BuildRequires to eclipse-platform

* Tue Jul 13 2004 Jeremy Handcock <handcock@redhat.com> 2.0-2
- Don't require ant
- Prevent possible `build' section overload

* Mon Jul 12 2004 Tom Tromey <tromey@redhat.com> 2.0-2
- Document source fetching process
- Update to CDT 2.0 final
- Set -D_GNU_SOURCE when building

* Fri Jul  9 2004 Tom Tromey <tromey@redhat.com> 2.0-2
- Don't define prefix
- Don't require pango

* Fri Jul  9 2004 Jeremy Handcock <handcock@redhat.com> 2.0-2
- Update sources to include tests from upstream
- Add new build patch for CDT tests
- Build CDT tests, but don't install them

* Thu Jul  8 2004 Tom Tromey <tromey@redhat.com> 2.0-1
- Removed unused patch

* Thu Jul  8 2004 Jeremy Handcock <handcock@redhat.com> 2.0-1
- Revert previous patch; don't unset javacVerbose

* Thu Jul  8 2004 Jeremy Handcock <handcock@redhat.com> 2.0-1
- Unset javacVerbose

* Tue Jun 15 2004 Tom Tromey <tromey@redhat.com> 2.0-1
- Updated to 2.0 M8

* Mon Jan 19 2004 Tom Tromey <tromey@redhat.com> 1.2.1-1
- Initial version
