Name:		mumble
Version:	1.2.5
Release:	1%{?dist}
Summary:	Voice chat suite aimed at gamers

Group:		Applications/Internet
License:	BSD
URL:		http://%{name}.sourceforge.net/
Source0:	http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
Source1:	murmur.service
Source2:	%{name}.desktop
Source5:	murmur-tmpfiles.conf
Patch0:		%{name}-1.2.5-slice2cpp.patch
Patch1:		%{name}-1.2.4-celt_include_dir.patch
# CVE-2012-0863
# https://github.com/mumble-voip/mumble/commit/5632c35d6759f5e13a7dfe78e4ee6403ff6a8e3e
Patch2:		0001-Explicitly-remove-file-permissions-for-settings-and-.patch
# Fix broken logrotate script (start-stop-daemon not available anymore), BZ 730129
Patch3:		mumble-1.2.3-logrotate.patch
Patch4:		mumble-fixspeechd.patch
# Upstream patch to fix hang on startup
# https://github.com/mumble-voip/mumble/commit/dee463ef52d8406d0a925facfabead616f0f9dc2
Patch5:		0001-bonjour-use-Qt-AutoConnection-for-BonjourServiceReso.patch

BuildRequires:	qt-devel, boost-devel, ice-devel
BuildRequires:	alsa-lib-devel
BuildRequires:	pulseaudio-libs-devel, speex-devel
BuildRequires:	speech-dispatcher-devel, libogg-devel
BuildRequires:	libcap-devel
BuildRequires:	desktop-file-utils, openssl-devel
BuildRequires:	libXevie-devel, celt071-devel
BuildRequires:	protobuf-compiler, avahi-compat-libdns_sd-devel
BuildRequires:	libsndfile-devel, protobuf-devel
BuildRequires:	opus-devel
Requires:	celt071
# Needed for tmpfiles.d service
Requires:	initscripts

# Due to missing ice on ppc64
ExcludeArch: ppc64

%description
Mumble provides low-latency, high-quality voice communication for gamers. 
It includes game linking, so voice from other players comes 
from the direction of their characters, and has echo 
cancellation so that the sound from your loudspeakers
won't be audible to other players.

%package -n murmur
Summary:	Mumble voice chat server
Group:		System Environment/Daemons
Provides:	%{name}-server = %{version}-%{release}

Requires(pre): shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires: qt4-sqlite

%description -n murmur
Murmur(also called mumble-server) is part of the VoIP suite Mumble
primarily aimed at gamers. Murmur is the server component of the suite.

%package plugins
Summary:	Plugins for VoIP program Mumble
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description plugins
Mumble-plugins is part of VoIP suite Mumble primarily intended 
for gamers. This plugin allows game linking so the voice of 
players will come from the direction of their characters.

%package overlay
Summary:	Start games with the mumble overlay
Group:		Applications/Internet
Requires:	%{name} = %{version}-%{release}

%description overlay
Mumble-overlay is part of the Mumble VoIP suite aimed at gamers. If supported,
starting your game with this script will enable an ingame Mumble overlay.

%package protocol
Summary:	Support for the mumble protocol
Group:		Applications/Internet
Requires:	%{name} = %{version}-%{release}	
Requires:	kde-filesystem

%description protocol
Mumble is a Low-latency, high-quality voice communication suite
for gamers. It includes game linking, so voice from other players
comes from the direction of their characters, and echo cancellation
so that the sound from your loudspeakers won't be audible to other players.

%pre -n murmur
getent group mumble-server >/dev/null || groupadd -r mumble-server
getent passwd mumble-server >/dev/null || \
useradd -r -g mumble-server -d %{_localstatedir}/lib/%{name}-server/ -s /sbin/nologin \
-c "Mumble-server(murmur) user" mumble-server
exit 0

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1 -F 2
%patch3 -p1
%patch4 -p1 -F 2
%patch5 -p1

%build
%{_qt4_qmake} "CONFIG+=no-bundled-speex no-g15 \
no-embed-qt-translations no-update \
no-bundled-celt no-bundled-opus packaged" \
QMAKE_CFLAGS_RELEASE="%{optflags}" \
QMAKE_CXXFLAGS_RELEASE="%{optflags}" \
DEFINES+="PLUGIN_PATH=%{_libdir}/%{name}" \
DEFINES+="DEFAULT_SOUNDSYSTEM=PulseAudio" main.pro
make release
#%{?_smp_mflags}

%install
install -pD -m0755 release/%{name} %{buildroot}%{_bindir}/%{name}
install -pD -m0755 release/murmurd %{buildroot}%{_sbindir}/murmurd
ln -s murmurd %{buildroot}%{_sbindir}/%{name}-server

#translations
mkdir -p %{buildroot}/%{_datadir}/%{name}/translations
install -pm 644 src/%{name}/*.qm %{buildroot}/%{_datadir}/%{name}/translations


mkdir -p %{buildroot}%{_libdir}/%{name}/
install -p release/libmumble.so.%{version} %{buildroot}%{_libdir}/%{name}/
install -p release/plugins/*.so %{buildroot}%{_libdir}/%{name}/
ln -s libmumble.so.%{version} %{buildroot}%{_libdir}/%{name}/libmumble.so
ln -s libmumble.so.%{version} %{buildroot}%{_libdir}/%{name}/libmumble.so.1
ln -s libmumble.so.%{version} %{buildroot}%{_libdir}/%{name}/libmumble.so.1.2

#symlink for celt071
ln -s ../libcelt071.so.0.0.0 %{buildroot}%{_libdir}/%{name}/libcelt.so.0.7.0

mkdir -p %{buildroot}%{_sysconfdir}/murmur/
install -pD scripts/murmur.ini.system %{buildroot}%{_sysconfdir}/murmur/murmur.ini
ln -s /etc/murmur/murmur.ini %{buildroot}%{_sysconfdir}/%{name}-server.ini
install -pD -m0644 %{SOURCE1} %{buildroot}%{_unitdir}/murmur.service

mkdir -p %{buildroot}%{_datadir}/%{name}/
install -pD scripts/%{name}-overlay %{buildroot}%{_bindir}/%{name}-overlay

#man pages
mkdir -p %{buildroot}%{_mandir}/man1/
install -pD -m0644 man/murmurd.1 %{buildroot}%{_mandir}/man1/
install -pD -m0644 man/mumble* %{buildroot}%{_mandir}/man1/
install -pD -m0664 man/mumble-overlay.1 %{buildroot}%{_mandir}/man1/mumble-overlay.1

#icons
mkdir -p %{buildroot}%{_datadir}/icons/%{name}
install -pD -m0644 icons/%{name}.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

#logrotate
install -pD scripts/murmur.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/murmur

# install desktop file
desktop-file-install --dir=%{buildroot}%{_datadir}/applications \
%{SOURCE2}

# install the mumble protocol
install -pD -m0644 scripts/%{name}.protocol %{buildroot}%{_datadir}/kde4/services/%{name}.protocol

# murmur.conf
install -pD -m0644 scripts/murmur.conf %{buildroot}%{_sysconfdir}/dbus-1/system.d/murmur.conf

#dir for mumble-server.sqlite
mkdir -p %{buildroot}%{_localstatedir}/lib/mumble-server/

#log dir
mkdir -p %{buildroot}%{_localstatedir}/log/mumble-server/

#pid dir
mkdir -p %{buildroot}%{_localstatedir}/run/
install -d -m 0710 %{buildroot}%{_localstatedir}/run/mumble-server/

#tmpfiles.d
mkdir -p %{buildroot}%{_sysconfdir}/tmpfiles.d
install -m 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/tmpfiles.d/%{name}.conf

%post
touch --no-create %{_datadir}/icons/hicolor &>/dev/null ||:

%postun 
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null ||:

%post -n murmur
%systemd_post murmur.service

%preun -n murmur
%systemd_preun murmur.service

%postun -n murmur
%systemd_postun_with_restart murmur.service

%files
%doc README README.Linux LICENSE CHANGES
%doc scripts/weblist*
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
%{_datadir}/applications/%{name}.desktop
%{_datadir}/mumble/
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/libcelt.so.0.7.0

%files -n murmur
%doc README README.Linux LICENSE CHANGES
%doc scripts/murmur.pl scripts/murmur-user-wrapper
%attr(-,mumble-server,mumble-server) %{_sbindir}/murmurd
%{_unitdir}/murmur.service
%{_sbindir}/%{name}-server
%config(noreplace) %attr(664,mumble-server,mumble-server) %{_sysconfdir}/murmur/murmur.ini
%config(noreplace) %attr(664,mumble-server,mumble-server) %{_sysconfdir}/mumble-server.ini
%{_mandir}/man1/murmurd.1*
%attr(664,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/murmur
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/murmur.conf
%dir %attr(-,mumble-server,mumble-server) %{_localstatedir}/lib/mumble-server/
%dir %attr(-,mumble-server,mumble-server) %{_localstatedir}/log/mumble-server/
%dir %attr(-,mumble-server,mumble-server) %{_localstatedir}/run/mumble-server/
%config(noreplace) %{_sysconfdir}/tmpfiles.d/%{name}.conf

%files plugins
%{_libdir}/%{name}/libmanual.so
%{_libdir}/%{name}/liblink.so

%files overlay
%{_bindir}/%{name}-overlay
%{_libdir}/%{name}/lib%{name}*
%{_mandir}/man1/mumble-overlay.1*

%files protocol
%{_datadir}/kde4/services/mumble.protocol

%changelog
* Tue Aug 27 2013 Christian Krause <chkr@fedoraproject.org> - 1.2.4-1
- Update 1.2.4 (BZ 976001)
- New systemd-rpm macros (BZ 850218)
- Cleanup

* Mon Aug 19 2013 Peter Robinson <pbrobinson@fedoraproject.org> 1.2.3-16
- Fix FTBFS due to speechd
- Drop alsa-oss support

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.3-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jul 30 2013 Petr Machata <pmachata@redhat.com> - 1.2.3-14
- Rebuild for boost 1.54.0

* Wed Apr 03 2013 Christian Krause <chkr@fedoraproject.org> - 1.2.3-13
- Rebuild against new ice package
- Updated Ice version in patch0

* Sun Mar 17 2013 Christian Krause <chkr@fedoraproject.org> - 1.2.3-12
- Rebuild against new protobuf package

* Wed Feb 06 2013 Christian Krause <chkr@fedoraproject.org> - 1.2.3-11
- Rebuild against new ice package
- Updated Ice version in patch0
- Use new systemd-rpm macros (BZ 850218)

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.3-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu May 31 2012 Christian Krause <chkr@fedoraproject.org> - 1.2.3-9
- Fix startup issues of murmurd (BZ 711711, BZ 770469, BZ 771423)
- Fix migration to systemd
  http://fedoraproject.org/wiki/Packaging:ScriptletSnippets#Systemd
- Fix directory ownership of %%{_libdir}/mumble and %%{_datadir}/mumble*
  (BZ 744886)
- Add upstream patch for CVE-2012-0863 (BZ 791058)
- Fix broken logrotate config file (BZ 730129)
- Add dependency for qt4-sqlite (BZ 660221)
- Remove /sbin/ldconfig from %%post(un) since mumble does not
  contain any libraries in %%{_libdir}
- Some minor cleanup

* Wed Apr 18 2012 Jon Ciesla <limburgher@gmail.com> - 1.2.3-8
- Migrate to systemd, BZ 790040.

* Fri Mar 16 2012 Tom Callaway <spot@fedoraproject.org> - 1.2.3-7
- rebuild against fixed ice

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.3-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Nov 10 2011 Andreas Osowski <th0br0@mkdir.name> - 1.2.3-5
- Updated Ice version in patch0
- Added new patch to build against celt071 includes thanks to Florent Le Coz

* Thu Nov 10 2011 Andreas Osowski <th0br0@mkdir.name> - 1.2.3-4
- rebuilt for protobuf update

* Mon Sep 12 2011 Andreas Osowski <th0br0@mkdir.name> - 1.2.3-3
- Rebuild for newer protobuf

* Tue May 17 2011 Andreas Osowski <th0br0@mkdir.name> - 1.2.3-2
- Added celt071 functionality
- Fixed the qmake args

* Wed Mar 30 2011 Andreas Osowski <th0br0@mkdir.name> - 1.2.3-1
- Update to 1.2.3
- Fixes vulnerability #610845
- Added patch to make it compile with Ice 3.4.0
- Added tmpfile.d config file for murmur

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.2-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Aug 25 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-10
- Actually removed the requirement for redhat-lsb

* Tue Aug 03 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-9
- Removed redhat-lsb from Requires for murmur
- Updated initscript for murmur

* Sun May 16 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-8
- Rebuild for protobuf ABI change
- Added redhat-lsb to the Requires for murmur

* Sun May  2 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-7
- Fixed murmur's init script

* Sun Apr 18 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-6
- Fix for missing dbus-qt-devel on >F12

* Sun Apr 18 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-5
- Merged Mary Ellen Foster's changelog entry

* Tue Mar 30 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-4
- Marked the files in /etc as config entries

* Tue Mar 23 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-3
- Added desktop file for mumble11x

* Mon Feb 22 2010 Julian Golderer <j.golderer@novij.at> - 1.2.2-2
- Added mumble11x
- Added svg icons
- Added language files

* Sun Feb 21 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-1
- Update to 1.2.2
