%define	name		BasiliskII
%define version		1.0
%define snapshot	20060501
%define release		%mkrel 0.%{snapshot}.5
%define mon_version	3.0
%define mon_snapshot	20030206
%define jit_arches	%{ix86} x86_64
# Current Mandrakelinux kernels have sheepnet driver integrated for
# both Basilisk II and MOL purposes
%define sheepnet	0
%define moduledir	/lib/modules
%define kernel_version	%(/bin/bash %{SOURCE5})
%define kver 		%(/bin/bash %{SOURCE5} | sed -e 's/-/./')

# (gb) use '%' instead of '$' so that the shell command is actually
# evaluated instead of being simply propagated in textual form
%define	modversion	%(uname -r)

# Define to print out some (debug) information when patching HW Bases
%define DebugHWBases	0

# Define to enable JIT_DEBUG
%define JITDebug	0

# Extract Mandriva Linux name
%if %{mdkversion} >= 1010
%define mdk_distro_file	/etc/release
%else
%define mdk_distro_file	/etc/mandrake-release
%endif
%define mdk_distro	%(perl -ne '/^([.\\w\\s]+) release/ and print $1' < %{mdk_distro_file})
 
Summary:		A free, portable Mac 68k emulator
Name:			%{name}
Version:		%{version}
Release:		%{release}
Requires(post,preun):			update-alternatives
Source0:		http://iphcip1.physik.uni-mainz.de/~cbauer/BasiliskII-%{version}-%{snapshot}.tar.bz2
Source1:		BasiliskII.16.png.bz2
Source2:		BasiliskII.32.png.bz2
Source3:		BasiliskII.48.png.bz2
Source4:		cxmon-%{mon_version}-%{mon_snapshot}.tar.bz2
Source5:		kernel-version.sh
Patch1:			BasiliskII-jit-debug-hwbases.patch.bz2
Patch2:			BasiliskII-1.0-sheepnet.patch.bz2
License:		GPLv2+
URL:			http://www.gibix.net/projects/basilisk2/
Group:			Emulators
BuildRoot:		%{_tmppath}/%{name}-%{version}-buildroot
BuildRequires:		gcc-c++
BuildRequires:		esound-devel libgtk+2.0-devel
Obsoletes:		BasiliskII-jit
Provides:		BasiliskII-jit

%description
Basilisk II is an Open Source 68k Macintosh emulator. That is, it enables
you to run 68k MacOS software on you computer, even if you are using a
different operating system. However, you still need a copy of MacOS and
a Macintosh ROM image to use Basilisk II (of course MacOS and Mac ROM
are not included in this package).

Some features of Basilisk II:
  - Emulates either a Mac Classic (which runs MacOS 0.x thru 7.5)
    or a Mac II series machine (which runs MacOS 7.x, 8.0 and 8.1),
    depending on the ROM being used
  - Color video display
  - CD quality sound output
  - Floppy disk driver (only 1.44MB disks supported)
  - Driver for HFS partitions and hardfiles
  - CD-ROM driver with basic audio functions
  - Easy file exchange with the host OS via a "Host Directory Tree" icon
    on the Mac desktop
  - Copy and paste text between MacOS and the host OS (X11 clipboard)
  - Ethernet driver
  - Serial drivers
  - SCSI Manager (old-style) emulation
  - Emulates extended ADB keyboard and 3-button mouse
%ifarch %{jit_arches}
This version also features a JIT ("Just In Time") compiler, which
speeds up the emulator by a factor of 10-15x with respect to the plain
version.
%endif

%if %{sheepnet}
%package sheepnet
Summary:	Basilisk II network module
Group:		System/Kernel and hardware
Requires:	%{name} = %{version}
Requires:	kernel-%{kver}

%description sheepnet
This package contains the sheep_net kernel module for
Ethernet networking under Basilisk II, suitable for
kernel %{kernel_version}.

%package sheepnet-smp
Summary:	Basilisk II network module
Group:		System/Kernel and hardware
Requires:	%{name} = %{version}
Requires:	kernel-smp-%{kver}

%description sheepnet-smp
This package contains the sheep_net kernel module for
Ethernet networking under Basilisk II, suitable for
kernel %{kernel_version}smp.

%package sheepnet-enterprise
Summary:	Basilisk II network module
Group:		System/Kernel and hardware
Requires:	%{name} = %{version}
Requires:	kernel-enterprise-%{kver}

%description sheepnet-enterprise
This package contains the sheep_net kernel module for
Ethernet networking under Basilisk II, suitable for
kernel %{kernel_version}enterprise.
%endif

%prep
%setup -q -a 4
perl -pi -e 's/^The XFree86 Project, Inc$/%{mdk_distro}/' src/Unix/keycodes
%if %{DebugHWBases}
%patch1 -p1 -b .hwbases
%endif
%if %{JITDebug}
perl -pi -e "s|([ \t]*mon_srcdir)=.*|\1=../../cxmon-%{mon_version}/src|" ./src/Unix/configure ./src/Unix/configure.in
%endif
%patch2 -p1 -b .sheepnet

%build
cd ./src/Unix
# Enable JIT compiler on x86 and x86-64
JIT_OPTIONS=
%ifarch %{jit_arches}
JIT_OPTIONS="--enable-jit-compiler"
%if %{JITDebug}
JIT_OPTIONS="$JIT_OPTIONS --with-mon --enable-jit-debug"
%endif
%endif
%configure2_5x $JIT_OPTIONS --with-gtk=gtk2
make obj
%make

%if %{sheepnet}
# build sheep_net module
cd Linux/NetDriver
make
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d -m 755 $RPM_BUILD_ROOT%{_bindir}
install -d -m 755 $RPM_BUILD_ROOT%{_libdir}
install -d -m 755 $RPM_BUILD_ROOT%{_mandir}/man1
%if %{sheepnet}
install -d -m 755 \
  $RPM_BUILD_ROOT%{moduledir}/%{kernel_version}/misc \
  $RPM_BUILD_ROOT%{moduledir}/%{kernel_version}smp/misc \
  $RPM_BUILD_ROOT%{moduledir}/%{kernel_version}enterprise/misc
%endif
cd ./src/Unix
%makeinstall

%if %{sheepnet}
# install the sheep_net module
cd ./Linux/NetDriver
install -m 644 sheep_net-up.o \
  $RPM_BUILD_ROOT%{moduledir}/%{kernel_version}/misc/sheep_net.o
install -m 644 sheep_net-smp.o \
  $RPM_BUILD_ROOT%{moduledir}/%{kernel_version}smp/misc/sheep_net.o
install -m 644 sheep_net-enterprise.o \
  $RPM_BUILD_ROOT%{moduledir}/%{kernel_version}enterprise/misc/sheep_net.o

# (gb) copy sources in case the module has to be rebuilt
install -d -m 755 $RPM_BUILD_ROOT/%{_datadir}/%{name}-sheepnet
install -m 644 Makefile $RPM_BUILD_ROOT/%{_datadir}/%{name}-sheepnet
install -m 644 sheep_net.c $RPM_BUILD_ROOT/%{_datadir}/%{name}-sheepnet
%endif

# mdk icons
mkdir -p $RPM_BUILD_ROOT%{_iconsdir}
mkdir -p $RPM_BUILD_ROOT%{_liconsdir}
mkdir -p $RPM_BUILD_ROOT%{_miconsdir}
bzcat %{SOURCE1} > $RPM_BUILD_ROOT%{_miconsdir}/%{name}.png
bzcat %{SOURCE2} > $RPM_BUILD_ROOT%{_iconsdir}/%{name}.png
bzcat %{SOURCE3} > $RPM_BUILD_ROOT%{_liconsdir}/%{name}.png

# mdk menu
mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications/
cat << EOF > %buildroot%{_datadir}/applications/mandriva-%{name}.desktop
[Desktop Entry]
Type=Application
Exec=%{_bindir}/%{name}
Name=Basilisk II
Categories=Emulator;
Icon=%{name}    
Comment=A Macintosh Emulator
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%if %mdkversion < 200900
%update_menus
%endif
update-alternatives --install %{_bindir}/basilisk2 basilisk2 %{_bindir}/%{name} 10 \
	--slave %{_mandir}/man1/basilisk2.1.bz2 basilisk2.1.bz2 %{_mandir}/man1/%{name}.1.bz2

%postun
%if %mdkversion < 200900
%clean_menus
%endif
[ $1 = 0 ] || exit 0
update-alternatives --remove basilisk2 %{_bindir}/%{name}

%if %{sheepnet}
%post sheepnet
/sbin/depmod -a || :

%postun sheepnet
if [ $1 = 0 ]; then
  if [ x`/sbin/lsmod | grep sheep_net | tr -s " " | cut -f 3 -d " "` == "x0" ]; then
    /sbin/rmmod sheep_net >/dev/null 2>&1
  fi
fi
/sbin/depmod -a || :

%post sheepnet-smp
/sbin/depmod -a || :

%postun sheepnet-smp
if [ $1 = 0 ]; then
  if [ x`/sbin/lsmod | grep sheep_net | tr -s " " | cut -f 3 -d " "` == "x0" ]; then
    /sbin/rmmod sheep_net >/dev/null 2>&1
  fi
fi
/sbin/depmod -a || :

%post sheepnet-enterprise
/sbin/depmod -a || :

%postun sheepnet-enterprise
if [ $1 = 0 ]; then
  if [ x`/sbin/lsmod | grep sheep_net | tr -s " " | cut -f 3 -d " "` == "x0" ]; then
    /sbin/rmmod sheep_net >/dev/null 2>&1
  fi
fi
/sbin/depmod -a || :
%endif

%files
%defattr(-,root,root)
# docs
%doc README TECH TODO COPYING ChangeLog
%{_mandir}/man1/%{name}.1*
#
%{_bindir}/BasiliskII
# data
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/fbdevices
%{_datadir}/%{name}/keycodes
%{_datadir}/%{name}/tunconfig
# mdk icons
%{_miconsdir}/%{name}.png*
%{_iconsdir}/%{name}.png*
%{_liconsdir}/%{name}.png*
# mdk menus
%{_datadir}/applications/mandriva-%{name}.desktop

%if %{sheepnet}
%files sheepnet
%defattr(-,root,root)
%dir %{_datadir}/%{name}-sheepnet
%{_datadir}/%{name}-sheepnet/Makefile
%{_datadir}/%{name}-sheepnet/sheep_net.c
%{moduledir}/%{kernel_version}/misc/*

%files sheepnet-smp
%defattr(-,root,root)
%{_datadir}/%{name}-sheepnet/Makefile
%{_datadir}/%{name}-sheepnet/sheep_net.c
%{moduledir}/%{kernel_version}smp/misc/*

%files sheepnet-enterprise
%defattr(-,root,root)
%{_datadir}/%{name}-sheepnet/Makefile
%{_datadir}/%{name}-sheepnet/sheep_net.c
%{moduledir}/%{kernel_version}enterprise/misc/*
%endif

