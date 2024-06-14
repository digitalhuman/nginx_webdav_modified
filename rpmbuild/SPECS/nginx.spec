Name:           nginx
Version:        1.27.0
Release:        1%{?dist}
Summary:        High performance web server

License:        BSD
URL:            http://nginx.org/
Source0:        http://nginx.org/download/nginx-%{version}.tar.gz
Source1:        nginx-dav-ext-module.tar.gz
Source2:        headers-more-nginx-module.tar.gz
Source3:        nginx.service
Source4:        auth.php

BuildRequires:  gcc
BuildRequires:  pcre-devel
BuildRequires:  zlib-devel
BuildRequires:  openssl-devel
BuildRequires:  libxml2-devel
BuildRequires:  libxslt-devel
BuildRequires:	perl-devel
BuildRequires:  perl-ExtUtils-Embed
BuildRequires:  GeoIP-devel
BuildRequires:  mariadb-devel

Requires:	pcre
Requires:	zlib
Requires:	openssl
Requires:	systemd
Requires:	php-fpm
Requires:	php-mysqlnd

Packager:	Victor Angelier BSCyS <victor@thecodingcompany.nl>

%description
Nginx is a high performance web server. This build is specific for WebDAV but has most common modules enabled.
Module list:
http_ssl_module \
http_dav_module \
http_xslt_module \
http_gzip_static_module \
http_geoip_module \
http_image_filter_module \
http_v2_module \
http_v3_module \
threads \
stream \
stream_ssl_module \
stream_geoip_module \
file-aio \
http_perl_module \
perl_modules_path=%{_libdir}/perl5/vendor_perl \
perl=%{_bindir}/perl \
module=$PWD/nginx-dav-ext-module \
module=$PWD/headers-more-nginx-module 


%prep
%setup -q
tar -xzf %{SOURCE1}
tar -xzf %{SOURCE2}

%build

# Configure and build Nginx with the Lua module
export PATH=$PATH:/usr/local/bin
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

CFLAGS="$CFLAGS -fPIE -fPIC" \
LDFLAGS="$LDFLAGS -pie" \
./configure --prefix=%{_prefix} \
            --sbin-path=%{_sbindir}/nginx \
            --conf-path=%{_sysconfdir}/nginx/nginx.conf \
            --pid-path=%{_localstatedir}/run/nginx.pid \
            --lock-path=%{_localstatedir}/lock/nginx.lock \
            --http-log-path=%{_localstatedir}/log/nginx/access.log \
            --error-log-path=%{_localstatedir}/log/nginx/error.log \
            --with-http_ssl_module \
            --with-http_dav_module \
            --with-http_xslt_module \
            --with-http_gzip_static_module \
            --with-http_geoip_module \
            --with-http_image_filter_module \
	    --with-http_auth_request_module \
            --with-http_v2_module \
	    --with-http_v3_module \
            --with-threads \
            --with-stream \
            --with-stream_ssl_module \
            --with-file-aio \
            --with-http_perl_module \
            --with-perl_modules_path=%{_libdir}/perl5/vendor_perl \
            --with-perl=%{_bindir}/perl \
	    --with-cc-opt="-I/usr/local/include" \
            --with-ld-opt="-L/usr/local/lib" \
            --add-module=$PWD/nginx-dav-ext-module \
            --add-module=$PWD/headers-more-nginx-module \

make

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

mkdir -p %{buildroot}/%{_sbindir}
mkdir -p %{buildroot}/%{_sysconfdir}/nginx
mkdir -p %{buildroot}/%{_sysconfdir}/nginx/conf.d
mkdir -p %{buildroot}/%{_localstatedir}/run
mkdir -p %{buildroot}/%{_localstatedir}/log/nginx
mkdir -p %{buildroot}/%{_datadir}/nginx/html
mkdir -p %{buildroot}/%{_unitdir}


# Install PHP auth file
install -m 644 %{SOURCE4} %{buildroot}/etc/nginx/conf.d/auth.php

# Move HTML files to the correct location
mv %{buildroot}/usr/html/* %{buildroot}/%{_datadir}/nginx/html

# Install the systemd service file
install -m 644 %{SOURCE3} %{buildroot}/%{_unitdir}/nginx.service


%pre
# Stop the service if it is running
if [ $1 -gt 1 ] ; then
    systemctl stop nginx.service >/dev/null 2>&1 || :
fi

%post
# Reload systemd configuration
systemctl daemon-reload >/dev/null 2>&1 || :

# Start the service
if [ $1 -eq 1 ] ; then
    systemctl start nginx.service >/dev/null 2>&1 || :
fi

# Enable the service
systemctl enable nginx.service >/dev/null 2>&1 || :

%preun
# Stop the service if it is being uninstalled
if [ $1 -eq 0 ] ; then
    systemctl stop nginx.service >/dev/null 2>&1 || :
    systemctl disable nginx.service >/dev/null 2>&1 || :
fi

%postun
# Reload systemd configuration
systemctl daemon-reload >/dev/null 2>&1 || :


%files
%{_sbindir}/nginx
%{_sysconfdir}/nginx
%{_localstatedir}/log/nginx
%{_datadir}/nginx/html/50x.html
%{_datadir}/nginx/html/index.html
/usr/lib64/perl5/vendor_perl/x86_64-linux-thread-multi/auto/nginx/nginx.so
/usr/lib64/perl5/vendor_perl/x86_64-linux-thread-multi/auto/nginx/.packlist
/usr/lib64/perl5/vendor_perl/x86_64-linux-thread-multi/nginx.pm
/usr/lib64/perl5/vendor_perl/x86_64-linux-thread-multi/perllocal.pod
/usr/lib64/perl5/vendor_perl/man3/nginx.3pm
%{_unitdir}/nginx.service
/usr/lib/debug/usr/lib64/perl5/vendor_perl/x86_64-linux-thread-multi/auto/nginx/nginx.so-1.27.0-1.el9.x86_64.debug
%config(noreplace) /etc/nginx/conf.d/auth.php

%changelog
* Thu Jun 14 2024 Victor Angelier BSCyS <victor@thecodingcompany.se> - 1.27.0-1
- Custom build with nginx-dav-ext-module

