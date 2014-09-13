%{!?__pecl:     %{expand: %%global __pecl     %{_bindir}/pecl}}
%global php_apiver  %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP API => //p') | tail -1)

%global basepkg   php54w
%global pecl_name memcache
%global with_zts  0%{?__ztsphp:1}

Summary:      Extension to work with the Memcached caching daemon
Name:         %{basepkg}-pecl-memcache
Version:      3.0.8
Release:      3%{?dist}
License:      PHP
Group:        Development/Languages
URL:          http://pecl.php.net/package/%{pecl_name}

Source:       http://pecl.php.net/get/%{pecl_name}-%{version}.tgz

Source2:      xml2changelog

BuildRoot:    %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: %{basepkg}-devel >= 4.3.11, %{basepkg}-pear, zlib-devel
Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Provides:     php-pecl-%{pecl_name} = %{version}-%{release}
Provides:     php-pecl(%{pecl_name}) = %{version}-%{release}
%if %{?php_zend_api}0
Requires:     php(zend-abi) = %{php_zend_api}
Requires:     php(api) = %{php_core_api}
%else
Requires:     php-api = %{php_apiver}
%endif

%if 0%{?fedora} < 20
# Filter shared private
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif

%description
Memcached is a caching daemon designed especially for
dynamic web applications to decrease database load by
storing objects in memory.

This extension allows you to work with memcached through
handy OO and procedural interfaces.

Memcache can be used as a PHP session handler.

%prep 
%setup -c -q
%{_bindir}/php %{SOURCE2} package.xml >CHANGELOG

%if %{with_zts}
cp -r %{pecl_name}-%{version} %{pecl_name}-%{version}-zts
%endif

%build

pushd %{pecl_name}-%{version}
phpize
%configure --with-php-config=%{_bindir}/php-config
%{__make} %{?_smp_mflags}
popd

%if %{with_zts}
pushd %{pecl_name}-%{version}-zts
zts-phpize
%configure --with-php-config=%{_bindir}/zts-php-config
%{__make} %{?_smp_mflags}
popd
%endif


%install
%{__rm} -rf %{buildroot}

pushd %{pecl_name}-%{version}
%{__make} install INSTALL_ROOT=%{buildroot}
popd

# Drop in the bit of configuration
%{__mkdir_p} %{buildroot}%{php_inidir}
%{__cat} > %{buildroot}%{php_inidir}/%{pecl_name}.ini << 'EOF'
; ----- Enable %{pecl_name} extension module
extension=%{pecl_name}.so

; ----- Options for the %{pecl_name} module

;  Whether to transparently failover to other servers on errors
;memcache.allow_failover=1
;  Data will be transferred in chunks of this size
;memcache.chunk_size=32768
;  Autocompress large data
;memcache.compress_threshold=20000
;  The default TCP port number to use when connecting to the memcached server 
;memcache.default_port=11211
;  Hash function {crc32, fnv}
;memcache.hash_function=crc32
;  Hash strategy {standard, consistent}
;memcache.hash_strategy=consistent
;  Defines how many servers to try when setting and getting data.
;memcache.max_failover_attempts=20
;  The protocol {ascii, binary} : You need a memcached >= 1.3.0 to use the binary protocol
;  The binary protocol results in less traffic and is more efficient
;memcache.protocol=ascii
;  Redundancy : When enabled the client sends requests to N servers in parallel
;memcache.redundancy=1
;memcache.session_redundancy=2
;  Lock Timeout
;memcache.lock_timeout = 15

; ----- Options to use the memcache session handler

;  Use memcache as a session handler
;session.save_handler=memcache
;  Defines a comma separated of server urls to use for session storage
;session.save_path="tcp://localhost:11211?persistent=1&weight=1&timeout=1&retry_interval=15"
EOF

%if %{with_zts}
pushd %{pecl_name}-%{version}-zts
%{__make} install INSTALL_ROOT=%{buildroot}
popd

# Drop in the bit of configuration
%{__mkdir_p} %{buildroot}%{php_ztsinidir}

%{__cp} %{buildroot}%{php_inidir}/%{pecl_name}.ini %{buildroot}%{php_ztsinidir}/%{pecl_name}.ini
%endif

# Install XML package description
# use 'name' rather than 'pecl_name' to avoid conflict with pear extensions
%{__mkdir_p} %{buildroot}%{pecl_xmldir}
%{__install} -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{pecl_name}.xml


%clean
%{__rm} -rf %{buildroot}


%if 0%{?pecl_install:1}
%post
%{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :
%endif


%if 0%{?pecl_uninstall:1}
%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi
%endif


%files
%defattr(-, root, root, -)
%doc CHANGELOG %{pecl_name}-%{version}/CREDITS %{pecl_name}-%{version}/README 
%doc %{pecl_name}-%{version}/example.php %{pecl_name}-%{version}/memcache.php
%config(noreplace) %{php_inidir}/%{pecl_name}.ini
%{php_extdir}/%{pecl_name}.so
%{pecl_xmldir}/%{pecl_name}.xml
%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{pecl_name}.ini
%{php_ztsextdir}/%{pecl_name}.so
%endif



%changelog
* Sat Sep 13 2014 Andy Thompson <andy@webtatic.com> 3.0.8-3
- Filter .so provides < EL7

* Sun Jul 14 2013 Andy Thompson <andy@webtatic.com> 3.0.8-2
- Add ZTS extension compilation

* Sat May 18 2013 Andy Thompson <andy@webtatic.com> 3.0.8-1
- update to 3.0.8
- Fix pecl xml location

* Mon Dec 24 2012 Andy Thompson <andy@webtatic.com> 3.0.7-1
- update to 3.0.7

* Sun Jul 22 2012 Andy Thompson <andy@webtatic.com> 3.0.6-1
- branch from php53-pecl-memcache
- update to 3.0.6

